import Head from "next/head";
import Image from "next/image";
import { useRouter } from "next/router";
import { useState, useEffect, useRef } from "react";
import {
  Input,
  Button,
  Radio,
  Form,
  Select,
  Upload,
  InputNumber,
  message,
  Divider,
  Card,
  Space,
  Row,
  Col,
} from "antd";
import FIleReader from "../components/FIleReader";

let backend_host = process.env.HOST_IP || "localhost:8000";
if (process.env.PRODUCTION === 'TRUE') {
  backend_host += '/api';
} 

const emoji_vendors = {
  Apple: "Appl",
  Google: "Goog",
  Meta: "FB",
  Windows: "Wind",
  Twitter: "Twtr",
  JoyPixels: "Joy",
  Samsung: "Sams",
};

export default function Home() {
  const formInitialValues = {
    canvas_type: "Rectangle",
    emoji_data: "",
    canvas_width: 78 * 10,
    canvas_height: 78 * 10,
    contour_width: 78 * 10,
    thold_alpha_contour: 10,
    thold_alpha_bb: 0,
    color: "white",
    contour_color: "(0, 172, 238, 255)",
    masked_file: { fileList: [] },
  };
  const [fileList, setFileList] = useState([]);
  const [sid, setSid] = useState();
  const [resultReady, setResultReady] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [resultMsg, setResultMsg] = useState();
  const [formValues, setFormValues] = useState(formInitialValues);
  const router = useRouter();

  const ws = useRef();
  const formRef = useRef();

  const startConnect = (callback) => {
    ws.current = new WebSocket(`ws://${backend_host}/plot`);
    ws.current.addEventListener("open", () => {
      console.log("ws opened");
      message.success("Connected to the server");
      if (callback) {
        callback(ws.current);
      }
    });
    ws.current.addEventListener("close", () => {
      message.warning("Connection closed");
      console.log("ws closed");
    });
    ws.current.addEventListener("message", (e) => {
      console.log("got ws message", e);
      const data = JSON.parse(e.data);
      if (data.e === "ready") {
        setResultReady(() => true);
        setProcessing(() => false);
        message.success("Finish processing");
        setResultMsg(data.msg);
        // router.push('/result?sid=' + sid);
      } else if (data.e === "sid") {
        setSid(data.data.sid);
        setResultReady(() => false);
        setProcessing(() => true);
        message.info("Start processing...");
      } else if (data.e === "process_error") {
        message.error(data.msg);
        setProcessing(() => false);
      }
    });
  };

  useEffect(() => {
    if (!ws.current) {
      startConnect();
    }
  }, []);

  console.log("render app", { formValues });

  const sendData = (ws, e, data) => {
    ws.send(JSON.stringify({ e, data: data }));
  };

  const handleSubmit = (e) => {
    console.log("form submit", formValues);
    console.log(e);
    if (ws.current.readyState === 3) {
      message.info("Connection closed. Reconnecting...");
      console.log("connection closed. restarting...");
      startConnect((ws) => {
        sendData(ws, 'plot', formValues);
      });
    } else {
      sendData(ws.current, 'plot', formValues);
    }
  };

  const handleFormChange = (e) => {
    console.log("form values change", e);
    setFormValues((old) => ({ ...old, ...e }));
  };

  const canvas_options = [
    { text: "Rectangle" },
    { text: "Ellipse" },
    { text: "Masked" },
  ];

  return (
    <div
      style={{
        margin: "2rem",
      }}
    >
      <Form
        layout="horizontal"
        onValuesChange={handleFormChange}
        onFinish={handleSubmit}
        labelCol={{
          span: 4,
        }}
        wrapperCol={{
          span: 16,
        }}
        initialValues={formInitialValues}
        ref={formRef}
      >
        <Space direction="vertical" size="middle" style={{ display: "flex" }}>
          <Card>
            <Space
              direction="vertical"
              size="small"
              style={{ display: "flex" }}
            >
              <Form.Item
                label="Canvas Type"
                name="canvas_type"
                rules={[{ required: true }]}
              >
                <Radio.Group>
                  {canvas_options.map((o, i) => (
                    <Radio key={i} value={o.text}>
                      {o.text}
                    </Radio>
                  ))}
                </Radio.Group>
              </Form.Item>

              {formValues.canvas_type === "Masked" && (
                <>
                  <Form.Item
                    label="Masked File"
                    name="masked_file"
                    rules={[{ required: true }]}
                  >
                    <Upload
                      action={`http://${backend_host}/upload`}
                      accept="image/png"
                      multiple={false}
                      defaultFileList={formValues.masked_file?.fileList || []}
                      onChange={(info) => {
                        if (info.file.status !== "uploading") {
                          console.log(info.file, info.fileList);
                        }

                        if (info.file.status === "done") {
                          message.success(
                            `${info.file.name} file uploaded successfully`
                          );
                          // console.log('after upload', info.file);
                          // handleFormChange({masked_file: info.file})
                          console.log("after file upload", fileList);
                        } else if (info.file.status === "error") {
                          message.error(
                            `${info.file.name} file upload failed.`
                          );
                        }
                      }}
                    >
                      {formValues.masked_file.fileList.length === 0 && (
                        <Button>Select an Image</Button>
                      )}
                    </Upload>
                  </Form.Item>
                  <Form.Item
                    label="Contour Width"
                    name="contour_width"
                    rules={[{ required: true }]}
                  >
                    <InputNumber />
                  </Form.Item>
                  <Form.Item label="Threshold Alpha" name="thold_alpha_contour">
                    <InputNumber placeholder="10" />
                  </Form.Item>
                  <Form.Item label="Threshold Alpha BB" name="thold_alpha_bb">
                    <InputNumber placeholder="0" />
                  </Form.Item>
                  <Form.Item
                    label="Contour Color"
                    name="contour_color"
                    wrapperCol={{ span: 8 }}
                  >
                    <Input placeholder="white" />
                  </Form.Item>
                </>
              )}

              {(formValues.canvas_type === "Rectangle" ||
                formValues.canvas_type === "Ellipse") && (
                <>
                  <Form.Item
                    label="Canvas Width"
                    name="canvas_width"
                    rules={[{ required: true }]}
                  >
                    <InputNumber />
                  </Form.Item>
                  <Form.Item
                    label="Canvas Height"
                    name="canvas_height"
                    rules={[{ required: true }]}
                  >
                    <InputNumber />
                  </Form.Item>
                  <Form.Item
                    label="Color"
                    name="color"
                    wrapperCol={{ span: 4 }}
                  >
                    <Input placeholder="white" />
                  </Form.Item>
                </>
              )}
            </Space>
          </Card>

          <Card>
            <Space
              direction="vertical"
              size="small"
              style={{ display: "flex" }}
            >
              <Form.Item
                label="Emoji Vendor"
                name="emoji_vendor"
                wrapperCol={{ span: 4 }}
                rules={[{ required: true }]}
              >
                <Select>
                  {Object.keys(emoji_vendors).map((key, i) => (
                    <Select.Option key={i} value={key}>
                      {key}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                label="Emoji Data"
                name="emoji_data"
                rules={[{ required: true }]}
              >
                <Input.TextArea
                  placeholder="Enter a Python dictionary here..."
                  style={{ height: "8rem" }}
                  className="code-textarea"
                />
              </Form.Item>
              <Row style={{ transform: "translateY(-5px)", marginBottom: '12px' }}>
                <Col offset={4}>
                  <FIleReader
                    onChange={(value) => {
                      console.log("filereader onchange", value);
                      let eData = {};
                      value.split("\n").map((line) => {
                        let t = line.trim().split(",");
                        if (t[0].trim() != "") {
                          eData[t[0].trim()] = parseInt(t[1].trim());
                        }
                      });
                      console.log("eData", eData);
                      console.log("formRef", formRef);
                      formRef.current.setFieldsValue({
                        emoji_data: JSON.stringify(eData),
                      });
                    }}
                    accept={".csv"}
                    text="Import from CSV"
                  ></FIleReader>
                </Col>
              </Row>
              <Row>
                <Col offset={4}>
                  <Button
                    size="large"
                    type="primary"
                    htmlType="submit"
                    disabled={processing}
                  >
                    Submit
                  </Button>
                </Col>
                <Col offset={2}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      height: "100%",
                    }}
                  >
                    {processing ? (
                      <div>
                        <span style={{marginRight: '2rem'}}>Processing......</span>
                        <Button onClick={() => {
                          sendData(ws.current, 'cancel');
                          setSid();
                          setProcessing(false);
                          setResultReady(false);
                          message.info('Processing cancelled');
                        }}>Cancel</Button>
                      </div>
                    ) : (
                      resultMsg && <span>{resultMsg}</span>
                    )}
                  </div>
                </Col>
              </Row>
              <Row>
                {resultReady && (
                  <div
                    style={{
                      margin: "1.5rem 1rem",
                      padding: "2rem",
                      width: "100%",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      background: "rgba(0,0,0,0.1)",
                    }}
                  >
                    <img
                      src={`http://${backend_host}/result/${sid}`}
                      style={{ width: "100%", maxWidth: "360px" }}
                    />
                  </div>
                )}
              </Row>
            </Space>
          </Card>
        </Space>
      </Form>
    </div>
  );
}
