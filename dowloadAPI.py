import requests
import glob
import os
import json
import zipfile
import pandas as pd
api_adress = 'http://54.249.71.234:5050'

def zipdir(imgpath,gtpath,  zipout):
    ziph = zipfile.ZipFile(zipout, "w", zipfile.ZIP_DEFLATED)
    allowExtend = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']

    for f in os.listdir(gtpath):
        if os.path.splitext(f)[-1] == 'txt':
            ziph.write(os.path.join(gtpath,f), os.path.join('gts',f))

    for f in os.listdir(imgpath):
        if os.path.splitext(f)[-1] in allowExtend:
            ziph.write(os.path.join(imgpath,f), os.path.join('imgs',f))

def zipdirImgs(imgpath, zipout):
    allowExtend = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']
    ziph = zipfile.ZipFile(zipout, "w", zipfile.ZIP_DEFLATED)
    for f in os.listdir(imgpath):
        if os.path.splitext(f)[-1] in allowExtend:
            ziph.write(os.path.join(imgpath,f), f)

def upload_file(filename):
    files = {'file': open(filename, 'rb')}
    r = requests.post(api_adress
                      + '/api/process'
                      , files=files, )
    print(r.json())
    return

# p = '/home/nhinhlap/nhinh/hoyu/tmp/error/65.15.jpg'
# upload_file(p)

def upload_gt_dir(dir_imgs, dir_gts, newName, progressBar=None):
    import time
    begin = time.time()
    zip_dir = ''
    zipPath = os.path.join(zip_dir, '{}.zip'.format(newName))
    zipdir(dir_imgs, dir_gts, zipPath)
    files = {'file': open(zipPath, 'rb')}
    res = requests.post(
        url=api_adress + '/api/upload_gtdir',
        files=files
    )
    num = len(os.listdir(dir_gts))
    print('upload {} files time: {}'.format(num * 2, time.time() - begin), res.status_code)
    os.remove(zipPath)
    return

# this want get os.path.listdir('/home/ubuntu/nhinhlt/train/crnn/datasets/syn_data')
def request_current_synDir():
    data = {'request': True}
    r = requests.post(api_adress + "/api/current_synDir", data=data )
    print(r.json())
    print('request_current_synDir done', r.status_code)
    return r.json(), None if r.status_code == 200 else 'server error' if r.status_code== 400 else 'Training is running'

def request_train_status():
    data = {'request': True}
    r = requests.post(api_adress + "/api/train_status", data=data)
    if r.status_code == 200 or r.status_code==201:
        ret = json.loads(r.json())
        ret = pd.DataFrame.from_dict(ret)
    else:
        ret = pd.DataFrame(columns=('name', 'loss', 'time', 'best', 'note'))

    print(ret)
    print('request_train_status done', r.status_code==200)
    return ret, r.status_code==200

def request_stop_training():
    data = {'request': True}
    r = requests.post(api_adress + "/api/stop_training", data=data)
    print('request_stop_training done:', r.status_code)
    return

# this want get os.path.listdir('/home/ubuntu/nhinhlt/train/crnn/datasets/syn_data')
# def request_all_checkpoints():
#     data = {'request': True}
    # r = requests.post(api_adress + "/api/all_checkpoints", data=data )
    # print('request_all_checkpoints done', r.status_code)
    # return r.json()

def request_all_checkpoints():
    data = {'request': True}
    r = requests.post(api_adress + "/api/train_status", data=data)
    if r.status_code == 200 or r.status_code==201:
        ret = json.loads(r.json())
        ret = pd.DataFrame.from_dict(ret)
    else:
        ret = pd.DataFrame(columns=('name', 'loss', 'time', 'best', 'note'))

    print(ret)
    print('request_train_status done', r.status_code==200)
    return ret

# this want sent list synDirs_chose to sever
def sent_synDirs_chose(synDirs_chose,IncrementalDir, pretrain, numEpoch, prefixName):
    data = {'chose': synDirs_chose, 'incremental_dir':str(IncrementalDir), 'pretrain':str(pretrain), 'numEpoch':numEpoch, 'prefixName': str(prefixName)}
    print(data)
    r = requests.post(api_adress + '/api/train', data=json.dumps(data), )
    print('sent_synDirs_chose done', r.status_code)
    return

def sent_checkpoint_chose(checkpoint_chose):
    data = {'chose': checkpoint_chose}
    r = requests.post(api_adress + '/api/checkpoint_chose', data=data)
    print('sent_checkpoint_chose done')
    print(r.json())
    return r.json()

def down_checkpoint_choseO(checkpoint_chose):
    data = {'chose': checkpoint_chose}
    r = requests.post(api_adress + '/api/down_checkpoint', data=data)
    # r = requests.post(api_adress + '/down_checkpoint', data=data)
    print('down_checkpoint_chose done')
    # print(r.json())
    return r

def down_checkpoint_chose(checkpoint_chose):
    data = {'chose': checkpoint_chose}
    r = requests.post(api_adress + '/api/down_checkpoint', data=data)
    # r = requests.post(api_adress + '/down_checkpoint', data=data)
    print('down_checkpoint_chose done')
    # print(r.json())

    return r, r.headers['filename']


def downloadHint(in_dir, out_dir, progressBar = None):
    import time
    begin = time.time()
    file_list = os.listdir(in_dir)
    import shutil
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    zip_dir = BASE_DIR
    zipPath = os.path.join(zip_dir, 'tmp.zip')
    zipdirImgs(in_dir, zipPath)
    print(zipPath)
    # try:
    files = {'file': open(zipPath, 'rb')}
    res = requests.post(
        url= api_adress + '/api/get_hint',
        files=files, timeout=1000000
    )
    data = res.json()
    # except ConnectionError:
    #     print('can not connect server')
    #     return 'can not connect server'
    # except:
    #     if progressBar is not None:
    #         progressBar.setRange(0, 10)
    #         progressBar.setLabelText('can not connect server')
    #         progressBar.delay()
    #     return
    if res.status_code == 200:
        for i, file in enumerate(data):
            name = os.path.splitext(file)[0] + '.txt'
            text = data[file]
            with open(os.path.join(out_dir, name), 'w') as w:
                w.write(text)

    print('process times {}: {} '.format(len(file_list), time.time() - begin), res.status_code)
    return res.status_code

# if __name__ == '__main__':
#
#     import time
#     bg = time.time()
#     # indirr = '/home/aimenext/nhinhlt/datasets/input/label_1601/tot/'
#     # out_dirr = '/home/aimenext/nhinhlt/datasets/input/label_1601/label'
#     indirr = ['/home/aimenext/nhinhlt/datasets/input/label_1601/tot/', '/home/aimenext/nhinhlt/datasets/input/label_1601/labeltot']
#     out_dirr = '/home/aimenext/nhinhlt/datasets/input/label_1601'
#
#     # main(indirr, out_dirr)
#     import shutil
#     #
#     # shutil.make_archive(out_dirr+'/test', 'zip', indirr)
#     # print(time.time() - bg)
#     # bg = time.time()
#     # shutil.unpack_archive(out_dirr+'/test.zip', extract_dir=out_dirr)
#
#     zipdir(indirr[0],indirr[1], os.path.join(out_dirr, 'tttt.zip'))
#
#     print(time.time() - bg)