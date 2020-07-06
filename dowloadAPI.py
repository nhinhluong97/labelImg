import requests
import glob
import os
import json
import zipfile
import shutil
import pandas as pd
import time

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'datasets')
# api_adress = 'http://54.249.71.234:5555'
api_adress = 'http://54.249.71.234:5050'

address_test_file = '/api/process'
address_upload_gt_dir = '/api/upload_gtdir'
address_current_synDir = "/api/current_synDir"
address_list_data_dir =  "/api/list_data_dir"
address_view_data =  "/api/view_data"
address_del_data =  "/api/del_data"
address_down_data =  "/api/down_data"
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
address_upload_charlist =  '/api/upload_charlist'

allowExtend = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']

def zipdirImgs(imgpath, zipout):
    # allowExtend = ['.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']
    ziph = zipfile.ZipFile(zipout, "w", zipfile.ZIP_DEFLATED)
    for f in os.listdir(imgpath):
        if os.path.splitext(f)[-1] in allowExtend:
            ziph.write(os.path.join(imgpath,f), f)
    ziph.close()

def upload_file(filename):
    files = {'file': open(filename, 'rb')}
    r = requests.post(api_adress
                      + address_test_file
                      , files=files, )
    return r

def zipdir(imgpath,gtpath,  zipout):
    global allowExtend
    ziph = zipfile.ZipFile(zipout, "w", zipfile.ZIP_DEFLATED)

    gts = os.listdir(gtpath)
    for f in os.listdir(imgpath):
        if os.path.splitext(f)[-1] in allowExtend and '{}.txt'.format(os.path.splitext(f)[0]) in gts:
            ziph.write(os.path.join(imgpath,f), os.path.join('imgs',f))
            ziph.write(os.path.join(gtpath, '{}.txt'.format(os.path.splitext(f)[0])), os.path.join('gts', '{}.txt'.format(os.path.splitext(f)[0])))
    ziph.close()

def request_current_synDir():
    data = {'request': True}
    r = requests.post(api_adress + address_current_synDir, data=data )
    print(r.json())
    print('request_current_synDir done', r.status_code)
    return r.json(), r.status_code

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
    # os.remove(zipPath)
    mess = None if res.status_code == 200 else res.json()['mess']
    return mess, res.status_code

def request_train(synDirs_chose, pretrain, numEpoch, prefixName, charlistName):
    data = {'chose': synDirs_chose, 'pretrain':str(pretrain), 'numEpoch':numEpoch,\
            'prefixName': str(prefixName), 'charlist': charlistName, 'syn_Ratio': 0.5, 'wiki_Ratio': 0.2}
    print(data)
    r = requests.post(api_adress + address_train, data=json.dumps(data), )
    print('request_train done', r.status_code)
    mess = None if r.status_code==200 else r.json()['mess']
    return mess , r.status_code

def upload_charlist(filename):
    files = {'file': open(filename, 'rb')}
    r = requests.post(api_adress
                      + address_upload_charlist
                      , files=files, )
    mess = None if r.status_code == 200 else r.json()['mess']
    return mess, r.status_code


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
        training_log = r.json()

    if r.status_code == 400:
        print(r.json(), r.status_code)

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
        curCpt = ret['curCpt']
    else:
        df = pd.DataFrame(columns=('name', 'loss', 'time', 'best', 'note'))
        curCpt = None

    listcheck = df['name']
    print('request_all_checkpoints done', r.status_code)
    return listcheck, curCpt, r.status_code


def sent_checkpoint_chose(checkpoint_chose):
    data = {'chose': checkpoint_chose}
    r = requests.post(api_adress + address_checkpoint_chose, data=data)
    print('sent_checkpoint_chose done')
    mess = None if r.status_code == 200 else r.json()['mess']
    return mess, r.status_code

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
    if not [f for f in os.listdir(in_dir) if os.path.splitext(f)[-1] in allowExtend]:
        return 200
    # try:
    zipPath = os.path.join(DATA_DIR, 'tmp.zip')
    zipdirImgs(in_dir, zipPath)
    files = {'file': open(zipPath, 'rb')}
    res = requests.post(
        url= api_adress + address_get_hint,
        files=files, timeout=1000000
    )

    # os.remove(zipPath)
    data = res.json()
    if res.status_code == 200:
        for i, file in enumerate(data):
            name = os.path.splitext(file)[0] + '.txt'
            text = data[file]
            with open(os.path.join(out_dir, name), 'w', encoding='utf-8') as w:
                w.write(text)

    print('process times {}: {} '.format(len(file_list), time.time() - begin), res.status_code)
    mess = None if res.status_code == 200 else res.json()['mess']
    return mess, res.status_code
    # except Exception as e:
    #     return e, 0

def request_list_data_dir():
    data = {'request': True}
    r = requests.post(api_adress + address_list_data_dir, data=data )
    print('request_list_data_dir done', r.status_code)
    return r.json(), r.status_code

def request_view_data():
    data = {'request': True}
    r = requests.post(api_adress + address_view_data, data=data)
    print('request_view_data done', r.status_code)
    ret = r.json()
    return ret, r.status_code

def request_del_data(folderName):
    data = {'request': True, 'dataname': folderName}
    r = requests.post(api_adress + address_del_data, data=data)
    print('request_del_data done', r.status_code)
    mess = None if r.status_code == 200 else r.json()['mess']
    return mess, r.status_code

def request_down_data(folderName, saveDir):
    data = {'request': True, 'dataname': folderName}
    # try:
    res = requests.post(api_adress + address_down_data, data=data)
    if res.status_code == 200:
        zip_checkpoint, filename = res, res.headers['filename']
        save_path = os.path.join(saveDir, filename)
        with open(save_path, 'wb') as f:
            for chunk in zip_checkpoint.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        shutil.unpack_archive(save_path, extract_dir=os.path.splitext(save_path)[0])

    print('request_down_data done', res.status_code)

    mess = None if res.status_code == 200 else res.json()['mess']
    return mess, res.status_code

    # except Exception as e:
    #     print(e)
    #     return e, 0

def downloadServerData(dataname, saveDir, data_refdir):
    import time
    begin = time.time()
    # try:
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
            shutil.rmtree(os.path.join(saveDir, dataname))
            shutil.move(imgs_path, os.path.join(saveDir, dataname))


        if  not os.path.exists(os.path.join(data_refdir, dataname)) :
            shutil.move(refs_path, os.path.join(data_refdir, dataname))
        else:
            shutil.rmtree(os.path.join(data_refdir, dataname))
            shutil.move(refs_path, os.path.join(data_refdir, dataname))

        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        # if os.path.exists(os.path.join(DATA_DIR, 'tmp.zip')):
        #     os.remove(os.path.join(DATA_DIR, 'tmp.zip'))

    print('process download: {} '.format(time.time() - begin), res.status_code)
    mess = None if res.status_code == 200 else res.json()['mess']
    return mess, res.status_code
    # except Exception as e:
    #     print(e)
    #     return e, 0

# if __name__ == '__main__':
#
#     import time
#     bg = time.time()
    # indirr = '/home/aimenext/nhinhlt/datasets/input/label_1601/tot/'
    # out_dirr = '/home/aimenext/nhinhlt/datasets/input/label_1601/label'
    # indirr = ['/home/aimenext/nhinhlt/datasets/input/label_1601/tot/', '/home/aimenext/nhinhlt/datasets/input/label_1601/labeltot']
    # out_dirr = '/home/aimenext/nhinhlt/datasets/input/label_1601'

    # main(indirr, out_dirr)
    # import shutil
    # #
    # shutil.make_archive(out_dirr+'/test', 'zip', indirr)
    # print(time.time() - bg)
    # bg = time.time()
    # shutil.unpack_archive(out_dirr+'/test.zip', extract_dir=out_dirr)
    #
    # # zipdir(indirr[0],indirr[1], os.path.join(out_dirr, 'tttt.zip'))
    #
    # print(time.time() - bg)

    # import faster_than_requests as requests
    #
    # requests.get("http://httpbin.org/get")  # GET
    # requests.post("http://httpbin.org/post", "Some Data Here")


if __name__ == '__main__':

    import time
    bg = time.time()
    indir = '/media/aimenext/data/nhinhlt/datasets/input/craft_data_281119/new_good/'
    out_dir = '/media/aimenext/data/nhinhlt/datasets/input/craft_data_281119/new_good/'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    imgs = [fn for fn in os.listdir(indir) if os.path.splitext(fn)[-1] != '.txt']
    print(imgs)
    num = len(imgs)
    for idx, fn in enumerate(imgs):

        fname = os.path.splitext(fn)[0]
        gtp = os.path.join(out_dir, '{}.txt'.format(fname))

        if not os.path.exists(os.path.join(indir, '{}.txt'.format(fname))):
            r = upload_file(os.path.join(indir, fn))
            if r.status_code == 200 and 'dict' in r.json():
                res = r.json()
                with open(gtp, 'w', encoding='utf-8') as gt:
                    data = res['dict']
                    data['brand'] = res['maker']
                    json.dump(data, gt, ensure_ascii=False, indent=4)
            else:
                print('error')
                with open(gtp, 'w', encoding='utf-8') as gt:
                    data = {}
                    json.dump(data, gt, ensure_ascii=False, indent=4)
            print('{}/{}:{}'.format(idx, num, fn))
