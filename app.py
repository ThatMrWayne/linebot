from flask import *
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextSendMessage, ImageSendMessage
)
from settings import CHANNEL_ACCESS_TOKEN
from settings import CHANNEL_SECRET
from settings import NGROK_URL
from model import db
import glob
import os


app = Flask(__name__)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
    if event.message.type == "text":
        if event.message.text == "圖片":
            image_name = db.get_image(event.source.user_id)
            if image_name == "error":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="不好意思,伺服器暫時有問題,請稍後再試"))
            elif image_name == "no image":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="您尚未傳送過圖片喔"))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url = NGROK_URL + "/static/" + image_name + "_" + event.source.user_id + '.png',
                        preview_image_url = NGROK_URL + "/static/" + image_name + "_" + event.source.user_id +'.png'
                    ))         
        else:    
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text))
    elif event.message.type == "image":
        set_image_result = db.set_image(event.source.user_id,event.message.id) 
        if set_image_result == "error":
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="不好意思,伺服器暫時有問題,請稍後再試"))
        elif set_image_result == 1:
            SendImage = line_bot_api.get_message_content(event.message.id)     
            path = './static/' + event.message.id + '_' + event.source.user_id + '.png'
            with open(path, 'wb') as fp:
                for chunk in SendImage.iter_content():
                    fp.write(chunk)
        elif set_image_result == 2:
            #delete original picture first
            old_pic = glob.glob(os.path.join("./static", "*_" + event.source.user_id + ".png"))[0]
            os.remove(old_pic)
            SendImage = line_bot_api.get_message_content(event.message.id)     
            path = './static/' + event.message.id + '_' + event.source.user_id + '.png'
            with open(path, 'wb') as fp:
                for chunk in SendImage.iter_content():
                    fp.write(chunk)




             

            
if __name__ == "__main__":
    app.run(host="0.0.0.0")
