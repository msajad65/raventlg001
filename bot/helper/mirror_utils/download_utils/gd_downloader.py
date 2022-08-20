from random import SystemRandom
from string import ascii_letters, digits

from bot import download_dict, download_dict_lock, LOGGER, STOP_DUPLICATE
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.mirror_utils.status_utils.gd_download_status import GdDownloadStatus
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage, sendFile
from bot.helper.ext_utils.fs_utils import get_base_name


def add_gd_download(link, path, listener, newname):
    res, size, name, files = GoogleDriveHelper().helper(link)
    if res != "":
        return sendMessage(res, listener.bot, listener.message)
    if newname:
        name = newname
    if STOP_DUPLICATE and not listener.isLeech:
        LOGGER.info('Checking File/Folder if already in Drive...')
        if listener.isZip:
            gname = f"{name}.zip"
        elif listener.extract:
            try:
                gname = get_base_name(name)
            except:
                gname = None
        if gname is not None:
            cap, f_name = GoogleDriveHelper().drive_list(gname, True)
            if cap:
                cap = f"‼️فایل یا پوشه موردنظر از قبل در درایو ما موجود است. نتایج جستجو در زیر قابل مشاهده است\n\n{cap}"
                sendFile(listener.bot, listener.message, f_name, cap)
                return
    LOGGER.info(f"Download Name: {name}")
    drive = GoogleDriveHelper(name, path, size, listener)
    gid = ''.join(SystemRandom().choices(ascii_letters + digits, k=12))
    download_status = GdDownloadStatus(drive, size, listener, gid)
    with download_dict_lock:
        download_dict[listener.uid] = download_status
    listener.onDownloadStart()
    sendStatusMessage(listener.message, listener.bot)
    drive.download(link)
