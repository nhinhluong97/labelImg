
import requests
import glob
import os
import json
import zipfile
import shutil
import cv2

# if __name__ == '__main__':
#     alldontknow = '/media/aimenext/data/nhinhlt/datasets/input/craft_data_281119/dontKnowHowAnnotates'
#     new_dont_know = '/media/aimenext/data/nhinhlt/datasets/input/craft_data_281119/new_dont_know/'
#     img_dir = '/media/aimenext/data/nhinhlt/datasets/input/craft_data_281119/media_not_train_remove_bad_imgs'
#
#     list_imgs = os.listdir(alldontknow)
#
#     if not os.path.exists(new_dont_know):
#         os.mkdir(new_dont_know)
#     #
#     imgs = [fn for fn in os.listdir(img_dir) if os.path.splitext(fn)[-1] != '.txt']
#     num = len(list_imgs)
#
#     for idx, fn in enumerate(list_imgs):
#         if fn in imgs:
#             fname = os.path.splitext(fn)[0]
#             shutil.move(os.path.join(img_dir, fn), os.path.join(new_dont_know, fn))
#             print('{}/{}:{}'.format(idx, num, fn))


def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default

def main(gt_path, gts_save):

    with open(gts_save, 'w', encoding='utf-8') as out_gt,\
            open(gt_path, 'r', encoding='utf-8') as in_gt:

                for line in in_gt:
                    line = line.strip('\n')
                    coor_text = ','.join(line.split(',')[:8])
                    lb = ','.join(line .split(',')[8:])
                    lbs = lb.split('|')
                    if '' in lbs:
                        lbs.remove('')
                    craft_lb = ''
                    if '###' in lbs[0]:
                        if len(lbs) > 2 and lbs[1].lower()=='craft':
                            craft_lb = lbs[2]
                            # craft_lb = 'A'*len(lbs[2])
                        else:
                            print('error ### in lbs[0]', lbs, fn)
                            continue
                    elif len(lbs) > 1 :
                        if 'v' in lbs[1]:
                            craft_lb = lbs[0]
                            # craft_lb = 'A'*len(lbs[0])
                            print('v in lbs[1]:', lbs, fn)
                        else:
                            print('error len(lbs) > 1 v not in lbs[1]', lbs, fn)
                            continue
                    else:
                        craft_lb = lbs[0]
                        # craft_lb = 'A'*len(lbs[0])
                    out_gt.write('{},{},{}\n'.format(coor_text,'Latin', craft_lb))
                    # 70,91,186,91,186,113,70,113,Latin,AAAAAA



if __name__ == '__main__':
    print('' in 'jhhgjfhgjkfh')
#
# if __name__ == '__main__':
#
#     indir = '/home/aimenext/nhinhlt/datasets/input/data_2306/FOR_CRAFT/craft_0307/annotate'
#     outdir = '/home/aimenext/nhinhlt/datasets/input/data_2306/FOR_CRAFT/craft_0307/gt'
#
#     if os.path.exists(outdir):
#         shutil.rmtree(outdir)
#     os.mkdir(outdir)
#
#     gts = os.listdir(indir)
#     for idx, fn in enumerate(gts):
#         gt_path = os.path.join(indir, fn)  #'/media/aimenext/data/nhinhlt/datasets/input/data_2306/FOR_CRAFT/data_1608011001235/1608011001179.txt'
#         gts_save = os.path.join(outdir, 'gt_{}'.format(fn))
#         main(gt_path, gts_save)
#
#         """"""

# if __name__ == '__main__':
#
#     val_new = '/home/aimenext/nhinhlt/dataset/classify_2306/validation'
#     classify_data_resize = '/home/aimenext/nhinhlt/dataset/classify_2306/classify_data_resize'
#
#     if os.path.exists(classify_data_resize):
#         shutil.rmtree(classify_data_resize)
#     os.mkdir(classify_data_resize)
#
#     list_dir = os.listdir(val_new)
#
#     for dir_name in list_dir:
#             src_path = os.path.join(val_new, dir_name)
#             dst_path = os.path.join(classify_data_resize, dir_name)
#             os.mkdir(dst_path)
#             imgs = os.listdir(src_path)
#             for fn in imgs:
#                 print(fn)
#                 try:
#                     img = cv2.imread(os.path.join(src_path, fn))
#                     img = cv2.resize(img, (640, 480))
#                     cv2.imwrite(os.path.join(dst_path, fn), img)
#                 except Exception as e:
#                     print('error:',e)

