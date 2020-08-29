#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import logging
from lottie.exporters.gif import  export_gif
from io import BytesIO
import lottie
import asyncio
from requests import get
import os
from moviepy import editor as mp
from pytube import YouTube
from pytube.helpers import safe_filename
from pdf2image import convert_from_path
from shutil import rmtree

FIRST, SECOND = range(2)
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
updater = Updater("TOKEEEEEEN", use_context=True)
dp = updater.dispatcher
msg_id = int()
def start(update, context):
    """Send message on `/start`."""
    user = update.message.from_user
    query = update.callback_query
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [InlineKeyboardButton("Stickers to jpg/gif", callback_data="stickers"),
         InlineKeyboardButton("Voice to .mp3", callback_data="voice")],
	 [InlineKeyboardButton("Video to .mp3", callback_data="video"),
	 InlineKeyboardButton("Video-circle to .mp4", callback_data="videonote")],
	 [InlineKeyboardButton("Youtube Download", callback_data="yt"),
	 InlineKeyboardButton("YT DL to .mp3", callback_data="ytmp3")],
	 [InlineKeyboardButton("PDF To JPEGs", callback_data="pdf_jpg"),
	 InlineKeyboardButton("Exit", callback_data="end")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    Message = update.message.reply_text(
        "Here we are! Choose a needed action.",
        reply_markup=reply_markup
    )
    global msg_id
    msg_id = Message.message_id
    return FIRST


def start_over(update, context):
    """Prompt same text & keyboard as `start` does but not as new message"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Stickers to jpg/gif", callback_data="stickers"),
         InlineKeyboardButton("Voice to .mp3", callback_data="voice")],
	 [InlineKeyboardButton("Video to .mp3", callback_data="video"),
	 InlineKeyboardButton("Video-circle to .mp4", callback_data="videonote")],
	 [InlineKeyboardButton("Youtube Download", callback_data="yt"),
	 InlineKeyboardButton("YT DL to .mp3", callback_data="ytmp3")],
	 [InlineKeyboardButton("PDF To JPEGs", callback_data="pdf_jpg"),
	 InlineKeyboardButton("Exit", callback_data="end")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Here we go again! Choose the action.",
        reply_markup=reply_markup
    )
    return FIRST


def stickers(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Home", callback_data="again"),
         InlineKeyboardButton("Exit", callback_data="end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You picked stickers section. Send sticker or press a button to go back. Note: Animated .gif from stickers may be buggy.",
        reply_markup=reply_markup
    )
    dp.add_handler(MessageHandler(Filters.sticker,sticker_start))
    return FIRST

def sticker_start(update, context):
			context.bot.send_message(chat_id=update.effective_chat.id, text="sticker!")
			stick = context.bot.getFile(update.message.sticker.file_id)
			if update.message.sticker.is_animated:
				context.bot.send_message(chat_id=update.effective_chat.id, text="Progressing animated sticker...")
				stick.download("sticker.tgs")
				fps = 60
				quality = 256

				anim = lottie.parsers.tgs.parse_tgs("sticker.tgs")
				result = BytesIO()
				result.name = "animation.gif"
				export_gif(anim, result,quality, 1)
				result.seek(0)
				context.bot.send_message(chat_id=update.effective_chat.id, text="Uploading...")
				context.bot.send_document(chat_id=update.message.chat_id, document = result, timeout = 1000)
				os.remove('sticker.tgs')
				os.remove('animation.gif')
			else:
				context.bot.send_message(chat_id=update.effective_chat.id, text="Progressing sticker...")
				stick.download("sticker.png")
				context.bot.send_document(chat_id=update.message.chat_id, document = open('sticker.png', 'rb'), timeout = 1000)
				os.remove('sticker.png')
			context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
			dp.delete_handler(MessageHandler(Filters.sticker,sticker_start))
			start(update,context)
			

def voice(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Home", callback_data="again"),
         InlineKeyboardButton("Exit", callback_data="end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You picked voice section. Send voice message or press a button to go back",
        reply_markup=reply_markup
    )
    dp.add_handler(MessageHandler(Filters.voice,voice_start))

    return FIRST

def voice_start(update, context):
	voice_file = context.bot.getFile(update.message.voice.file_id)
	context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading...")
	voice_file.download('voice.mp3')
	context.bot.send_document(chat_id=update.message.chat_id, document = open('voice.mp3', 'rb'), timeout = 1000)
	os.remove('voice.mp3')
	context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
	dp.delete_handler(MessageHandler(Filters.voice,voice_start))
	start(update,context)
def video(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Home", callback_data="again"),
         InlineKeyboardButton("Exit", callback_data="end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You picked video section. Send video message to convert to mp3 or press a button to go back",
        reply_markup=reply_markup
    )
    dp.add_handler(MessageHandler(Filters.video, video_start))

    return FIRST

def video_start(update, context):
	video_file = context.bot.getFile(update.message.video.file_id)
	context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading...")
	video_file.download('video.mp4')
	context.bot.send_message(chat_id=update.effective_chat.id, text="Doing magic...")
	clip = mp.VideoFileClip('video.mp4')
	clip.audio.write_audiofile(f'video.mp3')
	context.bot.send_document(chat_id=update.message.chat_id, document = open('video.mp3', 'rb'), timeout = 1000)
	os.remove('video.mp3')
	os.remove('video.mp4')
	context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
	dp.delete_handler(MessageHandler(Filters.video, video_start))
	start(update,context)

def videonote(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Home", callback_data="again"),
         InlineKeyboardButton("Exit", callback_data="end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You picked video_note section. Send video message in circle to convert to mp4 or press a button to go back",
        reply_markup=reply_markup
    )
    dp.add_handler(MessageHandler(Filters.video_note, videonote_start))

    return FIRST

def videonote_start(update, context):
	videonote_file = context.bot.getFile(update.message.video_note.file_id)
	context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading...")
	videonote_file.download('video.mp4')
	context.bot.send_document(chat_id=update.message.chat_id, document = open('video.mp4', 'rb'), timeout = 1000)
	context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
	dp.delete_handler(MessageHandler(Filters.video_note, videonote_start))
	start(update,context)

def yt(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Home", callback_data="again"),
         InlineKeyboardButton("Exit", callback_data="end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You picked Youtube Download section. Send message with link to download or press a button to go back. May not download all videos.",
        reply_markup=reply_markup
    )
    dp.add_handler(MessageHandler(Filters.text, yt_start))

    return FIRST

def yt_start(update, context):
	link = update.message.text
	video = YouTube(link)
	video_stream = video.streams.filter(progressive=True,subtype="mp4").first()
	video_size = video_stream.filesize / 1000000
	if video_size >= 50:
		context.bot.send_message(chat_id=update.effective_chat.id, text= "**File larger than 50MB. Sending the link instead.\n**"
             														f"Get the video [here]({video_stream.url})\n\n"
             														"**If the video plays instead of downloading, "
															"right click(or long press on touchscreen) and "
															"press 'Save Video As...'(may depend on the browser) "
															"to download the video.**")

	else:
		context.bot.send_message(chat_id=update.effective_chat.id, text= "Downloading...")
		video_stream.download(filename="videoyt")
		url = f"https://img.youtube.com/vi/{video.video_id}/maxresdefault.jpg"
		resp = get(url)
		with open('thumbnail.jpg', 'wb') as file:
			file.write(resp.content)
		context.bot.send_document(chat_id=update.effective_chat.id, document = open("videoyt.mp4", 'rb'), caption=f"{video.title}", thumb="thumbnail.jpg")
		os.remove(f"videoyt.mp4")
		os.remove('thumbnail.jpg')

	context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
	dp.delete_handler(MessageHandler(Filters.text, yt_start))
	start(update,context)

def ytmp3(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Home", callback_data="again"),
         InlineKeyboardButton("Exit", callback_data="end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You picked Youtube Download to mp3 section. Send message with link to download and convert to mp3 or press a button to go back. May not download all videos.",
        reply_markup=reply_markup
    )
    dp.add_handler(MessageHandler(Filters.text, ytmp3_start))

    return FIRST

def ytmp3_start(update, context):
	link = update.message.text
	video = YouTube(link)
	video_stream = video.streams.filter(progressive=True,subtype="mp4").first()
	context.bot.send_message(chat_id=update.effective_chat.id, text= "Downloading...")
	video_stream.download(filename="videoyt")
	url = f"https://img.youtube.com/vi/{video.video_id}/maxresdefault.jpg"
	resp = get(url)
	with open('thumbnail.jpg', 'wb') as file:
		file.write(resp.content)
	context.bot.send_message(chat_id=update.effective_chat.id, text="Doing magic...")
	clip = mp.VideoFileClip('videoyt.mp4')
	clip.audio.write_audiofile(f'videoyt.mp3')
	context.bot.send_document(chat_id=update.effective_chat.id, document = open("videoyt.mp3", 'rb'), caption=f"{video.title}", thumb="thumbnail.jpg")
	os.remove(f"videoyt.mp4")
	os.remove(f"videoyt.mp3")
	os.remove('thumbnail.jpg')
	context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
	dp.delete_handler(MessageHandler(Filters.text, ytmp3_start))
	start(update,context)

def pdf_jpg(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Home", callback_data="again"),
         InlineKeyboardButton("Exit", callback_data="end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You picked PDF to JPEG section. Send PDF file to convert to JPEGs or press a button to go back",
        reply_markup=reply_markup
    )
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), pdf_jpg_start))

    return FIRST

def pdf_jpg_start(update, context):
	pdf_file = context.bot.getFile(update.message.document.file_id)
	context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading...")
	pdf_file.download('/home/ober0n/file.pdf') 
	if os.path.isdir("/home/ober0n/files") is False:
		os.mkdir("/home/ober0n/files")
	images_from_path = convert_from_path('/home/ober0n/file.pdf', output_folder='/home/ober0n/files/', fmt='png')
	for filename in os.listdir("/home/ober0n/files"):
		context.bot.send_document(chat_id=update.message.chat_id, document = open('/home/ober0n/files/' + filename, 'rb'), timeout = 1000)
	rmtree("/home/ober0n/files")
	os.remove(f"/home/ober0n/file.pdf")
	context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
	dp.delete_handler(MessageHandler(Filters.document.mime_type("application/pdf"), pdf_jpg_start))
	start(update,context)
	return FIRST

def end(update, context):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="See you next time, when you'll type /start *Windows xp shutdown sound*"
    )
    return ConversationHandler.END


def main():

    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
		#How to in one state????
            FIRST:[CallbackQueryHandler(stickers, pattern='^' + "stickers" + '$'),
                    CallbackQueryHandler(start, pattern='^' + "start" + '$'),
                    CallbackQueryHandler(video, pattern='^' + "video" + '$'),
                    CallbackQueryHandler(videonote, pattern='^' + "videonote" + '$'),
                    CallbackQueryHandler(voice, pattern='^' + "voice" + '$'),
                    CallbackQueryHandler(yt, pattern='^' + "yt" + '$'),
                    CallbackQueryHandler(pdf_jpg, pattern='^' + "pdf_jpg" + '$'),
                    CallbackQueryHandler(end, pattern='^' + "end" + '$'),
                    CallbackQueryHandler(start_over, pattern='^' + "again" + '$'),
                    CallbackQueryHandler(ytmp3, pattern='^' + "ytmp3" + '$')],
            SECOND: [CallbackQueryHandler(start_over, pattern='^' + "again" + '$'),
                     CallbackQueryHandler(end, pattern='^' + "end" + '$')]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
