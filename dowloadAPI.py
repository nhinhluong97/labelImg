import requests
import glob
import os
import json
import zipfile
import shutil
import pandas as pd

DATA_DIR = './datasets'

# api_adress = 'http://54.249.71.234:5555'
api_adress = 'http://54.249.71.234:5050'

address_test_file = '/api/process'
address_upload_gt_dir = '/api/upload_gtdir'
address_current_synDir = "/api/current_synDir"
address_list_data_dir =  "/api/list_data_dir"
address_train_status =  "/api/train_status"
address_trainning_history =  "/api/trainning_history"
address_trainning_log =  "/api/trainning_log"
address_stop_training =  "/api/stop_training"
address_save_notes =  '/api/save_notes'
address_train =  '/api/train'
address_checkpoint_chose =  '/api/checkpoint_chose'
address_down_checkpoint =  '/api/down_checkpoint2'
address_get_hint =  '/api/get_hint'
download_Server_Data =  '/api/download_Server_Data'

allowExtend = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']
def zipdir(imgpath,gtpath,  zipout):
    global allowExtend
    ziph = zipfile.ZipFile(zipout, "w", zipfile.ZIP_DEFLATED)

    for f in os.listdir(gtpath):
        if os.path.splitext(f)[-1] == '.txt':
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
                      + address_test_file
                      , files=files, )
    print(r.json())
    return

def upload_gt_dir(dir_imgs, dir_gts, newName):
    import time
    begin = time.time()
    zipPath = os.path.join(DATA_DIR, '{}.zip'.format(newName))
    zipdir(dir_imgs, dir_gts, zipPath)
    files = {'file': open(zipPath, 'rb')}
    res = requests.post(
        url=api_adress + address_upload_gt_dir,
        files=files
    )
    num = len(os.listdir(dir_gts))
    print('upload {} files time: {}'.format(num * 2, time.time() - begin), res.status_code)
    os.remove(zipPath)
    return res.status_code

def request_current_synDir():
    data = {'request': True}
    r = requests.post(api_adress + address_current_synDir, data=data )
    print(r.json())
    print('request_current_synDir done', r.status_code)
    return r.json(), r.status_code

def request_list_data_dir():
    data = {'request': True}
    r = requests.post(api_adress + address_list_data_dir, data=data )
    # print(r.json())
    print('request_list_data_dir done', r.status_code)
    return r.json(), r.status_code

def request_train_status():
    data = {'request': True}
    r = requests.post(api_adress + address_train_status, data=data)
    if r.status_code == 200 or r.status_code==201:
        ret = r.json()
        df = json.loads(ret['df'])
        training_log = ret['training_log']
        df = pd.DataFrame.from_dict(df)
    else:
        df = pd.DataFrame(columns=('name', 'loss', 'time', 'best', 'note'))
        training_log = None
    print('request_train_status done', r.status_code)
    print('training_log',training_log)
    return df, training_log, r.status_code

def request_trainning_history(cpt_name):
    data = {'cpt_name': cpt_name}
    r = requests.post(api_adress + address_trainning_history, data=data)
    if r.status_code == 200 or r.status_code == 201:
        ret = json.loads(r.json())
        ret = pd.DataFrame.from_dict(ret)
    else:
        ret = pd.DataFrame(columns=('name', 'loss', 'time', 'best', 'note'))

    print('request_trainning_history done:', r.status_code)
    return ret, r.status_code

def request_current_trainning_log():
    data = {'request': True}
    r = requests.post(api_adress + address_trainning_log, data=data)
    if r.status_code == 200:
        ret = r.json()
        df = json.loads(ret['df'])
        training_log = ret['training_log']
        df = pd.DataFrame.from_dict(df)
    else:
        df = pd.DataFrame(columns=('name', 'loss', 'time', 'best', 'note'))
        training_log = None

    print('request_current_trainning_log done:', r.status_code)
    return df, training_log, r.status_code

def request_stop_training():
    data = {'request': True}
    r = requests.post(api_adress + address_stop_training, data=data)
    print('request_stop_training done:', r.status_code)
    return r.status_code


def request_save_notes(notes, dir_path):
    data = {'notes': notes, 'dir_path': dir_path}
    print(data)
    r = requests.post(api_adress + address_save_notes, data=json.dumps(data))
    print('request_save_notes done', r.status_code)
    return r.status_code

def request_all_checkpoints():
    data = {'request': True}
    r = requests.post(api_adress + address_train_status, data=data)
    if r.status_code == 200 or r.status_code == 201:
        ret = r.json()
        df = json.loads(ret['df'])
        df = pd.DataFrame.from_dict(df)
    else:
        df = pd.DataFrame(columns=('name', 'loss', 'time', 'best', 'note'))

    listcheck = df['name']
    print('request_all_checkpoints done', r.status_code)
    return listcheck, r.status_code

# this want sent list synDirs_chose to sever
def sent_synDirs_chose(synDirs_chose, pretrain, numEpoch, prefixName):
    data = {'chose': synDirs_chose, 'pretrain':str(pretrain), 'numEpoch':numEpoch, 'prefixName': str(prefixName)}
    print(data)
    r = requests.post(api_adress + address_train, data=json.dumps(data), )
    print('sent_synDirs_chose done', r.status_code)
    return r.status_code

def sent_checkpoint_chose(checkpoint_chose):
    data = {'chose': checkpoint_chose}
    r = requests.post(api_adress + address_checkpoint_chose, data=data)
    print('sent_checkpoint_chose done')
    if r.status_code==400:
        print(r.json())
    return r.status_code

def down_checkpoint_chose(checkpoint_chose):
    data = {'chose': checkpoint_chose}
    r = requests.post(api_adress + address_down_checkpoint, data=data)
    # r = requests.post(api_adress + '/down_checkpoint', data=data)
    print('down_checkpoint_chose done')
    # print(r.json())
    if r.status_code==200:
        return r, r.headers['filename'], r.status_code
    else:
        return None, None, r.status_code

def downloadHint(in_dir, out_dir):
    import time
    begin = time.time()
    file_list = os.listdir(in_dir)
    zipPath = os.path.join(DATA_DIR, 'tmp.zip')
    zipdirImgs(in_dir, zipPath)
    # try:
    files = {'file': open(zipPath, 'rb')}
    res = requests.post(
        url= api_adress + address_get_hint,
        files=files, timeout=1000000
    )
    os.remove(zipPath)

    data = res.json()
    if res.status_code == 200:
        for i, file in enumerate(data):
            name = os.path.splitext(file)[0] + '.txt'
            text = data[file]
            with open(os.path.join(out_dir, name), 'w') as w:
                w.write(text)

    print('process times {}: {} '.format(len(file_list), time.time() - begin), res.status_code)
    return res.status_code


def downloadServerData(dataname, saveDir, data_refdir):
    import time
    begin = time.time()
    try:
        data = {'dataname': dataname}
        res = requests.post(api_adress + download_Server_Data, data=data)

        if res.status_code == 200:
            zip_checkpoint, filename = res, res.headers['filename']
            save_path = os.path.join(DATA_DIR, 'tmp.zip')
            if save_path:
                with open(save_path, 'wb') as f:
                    for chunk in zip_checkpoint.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            shutil.unpack_archive(save_path, extract_dir= os.path.splitext(save_path)[0])
            save_path = os.path.splitext(save_path)[0]

            imgs_path = os.path.join(save_path, 'imgs.zip')
            shutil.unpack_archive(imgs_path, extract_dir=os.path.splitext(imgs_path)[0])
            imgs_path = os.path.join(save_path, 'imgs')

            refs_path = os.path.join(save_path, 'refs.zip')
            shutil.unpack_archive(refs_path, extract_dir=os.path.splitext(refs_path)[0])
            refs_path = os.path.join(save_path, 'refs')

            if not os.path.exists(os.path.join(saveDir, dataname)) :
                shutil.move(imgs_path, os.path.join(saveDir, dataname))
            else:
                imgs = os.listdir(imgs_path)
                for fn in imgs:
                    shutil.move(os.path.join(imgs_path, fn), os.path.join(saveDir, dataname))


            if  not os.path.exists(os.path.join(data_refdir, dataname)) :
                shutil.move(refs_path, os.path.join(data_refdir, dataname))
            else:
                gts = os.listdir(refs_path)
                for fn in gts:
                    shutil.move(os.path.join(refs_path, fn), os.path.join(data_refdir, dataname))
            if os.path.exists(save_path):
                shutil.rmtree(save_path)
            if os.path.exists(os.path.join(DATA_DIR, 'tmp.zip')):
                os.remove(os.path.join(DATA_DIR, 'tmp.zip'))

        print('process download: {} '.format(time.time() - begin), res.status_code)
        return res.status_code
    except Exception as e:
        print(e)



#
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
#     shutil.make_archive(out_dirr+'/test', 'zip', indirr)
#     print(time.time() - bg)
#     bg = time.time()
#     shutil.unpack_archive(out_dirr+'/test.zip', extract_dir=out_dirr)
#
#     # zipdir(indirr[0],indirr[1], os.path.join(out_dirr, 'tttt.zip'))
#
#     print(time.time() - bg)