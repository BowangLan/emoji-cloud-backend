
## Run

Start the backend:

```
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload && celery -A mycelery worker --loglevel=info
```

Start the frontend:

```
npm run build && npm start
```

Start the web server:

```
redis-server
service nginx restart
```

## Folder Structure

The `EmojiCloud` folder under the root folder is clone directly from the Github repo. 

* Inside `EmojiCloud/Emojicloud` contains changes I made to the package itself.
* `EmojiCloud/demo1.py` tests the package using the original `EmojiCloud.py` file.
* `EmojiCloud/demo1.py` tests the package using the refactored files and folders.


