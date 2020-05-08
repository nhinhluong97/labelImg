if __name__ == '__main__':

    import time
    bg = time.time()
    indirr = '/home/aimenext/nhinhlt/datasets/input/label_1601/tot/'
    out_dirr = '/home/aimenext/nhinhlt/datasets/input/label_1601/label'
    # indirr = ['/home/aimenext/nhinhlt/datasets/input/label_1601/tot/'] #, '/home/aimenext/nhinhlt/datasets/input/label_1601/labeltot']
    # out_dirr = '/home/aimenext/nhinhlt/datasets/input/label_1601'

    # main(indirr, out_dirr)
    import shutil
    #
    shutil.make_archive(out_dirr+'/test', 'zip', indirr)
    print(time.time() - bg)
    bg = time.time()
    shutil.unpack_archive(out_dirr+'/test.zip', extract_dir=out_dirr)

    # zipdir(indirr[0],indirr[1], os.path.join(out_dirr, 'tttt.zip'))

    print(time.time() - bg)