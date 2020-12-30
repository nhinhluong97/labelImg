import os
import cv2
import shutil

def convert_jpg(indir, outdir):

    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)

    imgs = os.listdir(indir)
    for idx, fn in enumerate(imgs):
        print('{}/{}:{}'.format(idx, len(imgs), fn))
        basename = os.path.splitext(fn)[0]
        img_path = os.path.join(indir, fn)
        img = cv2.imread(img_path)
        savep = os.path.join(outdir, '{}.png'.format(basename))
        cv2.imwrite(savep, img)


if __name__ == '__main__':
    indir = '/home/aimenext/nhinhlt/infordio_datasets/20200923_AIME様向けサンプル帳票_TIF'
    outdir = '/home/aimenext/nhinhlt/infordio_datasets/20200923_AIME様向けサンプル帳票'
    convert_jpg(indir, outdir)