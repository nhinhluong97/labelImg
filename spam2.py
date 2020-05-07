# import pandas as pd
import random
#
# from PIL import Image
# import scipy
#
# # import png
# imggen_train.on_train_begin()
#
# result = imggen_train.next_train()
#
# log_dir = 'debug/'
# if not os.path.exists(log_dir):
#     os.makedirs(log_dir)
# for i in range(5):
#     print("------------------------------------{}----------------------------------".format(i))
#     inputs, outputs = next(result)
#     print(inputs["the_input"].shape, inputs["the_input"][0].shape)
#
#     # return
#
#     # print (len(inputs["the_labels"]), len(outputs))
#
#     # print (inputs["source_str"])
#
#     for idx, img in enumerate(inputs["the_input"]):
#         img = (img * 255).astype("uint8")
#
#         # print (img.shape)
#         img = np.squeeze(img)
#
#         # img = img.transpose([1,0,2])
#         img = img.T
#
#         print('{}/{}_{}.png'.format(log_dir, i, idx))
#         im = Image.fromarray(img)
#         # im.save('/home/vsocr/phong_nd_from_server1/log_img_training/crnn/debug/update_date/{}_{}.png'.format(i,idx))
#         im.save(
#             '{}/{}_{}_real.png'.format(log_dir, i, idx))
# # # scipy.misc.imsave('{}.jpg'.format(idx), img)
#
# # f = open('debug/{}.png'.format(idx), 'wb')      # binary mode is important
# # w = png.Writer(img.shape[1], img.shape[0], greyscale=True)
# # w.write(f, img)
# # f.close()
#
# return

if __name__ == '__main__':

    print('*'*7)
    # from PIL import Image
    # import scipy
    # # import png
    # imggen_train.on_train_begin()
    #
    # result = imggen_train.next_train()
    #
    # log_dir = 'debug/'
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)
    # for i in range(5):
    #     print("------------------------------------{}----------------------------------".format(i))
    #     inputs, outputs = next(result)
    #     print(inputs["the_input"].shape, inputs["the_input"][0].shape)
    #
    #     # return
    #
    #     # print (len(inputs["the_labels"]), len(outputs))
    #
    #     # print (inputs["source_str"])
    #
    #     for idx, img in enumerate(inputs["the_input"]):
    #         img = (img * 255).astype("uint8")
    #
    #         # print (img.shape)
    #         img = np.squeeze(img)
    #
    #         # img = img.transpose([1,0,2])
    #         img = img.T
    #
    #         print('{}/{}_{}.png'.format(log_dir, i, idx))
    #         im = Image.fromarray(img)
    #         # im.save('/home/vsocr/phong_nd_from_server1/log_img_training/crnn/debug/update_date/{}_{}.png'.format(i,idx))
    #         im.save(
    #             '{}/{}_{}_real.png'.format(log_dir, i, idx))
    # # # scipy.misc.imsave('{}.jpg'.format(idx), img)
    #
    # # f = open('debug/{}.png'.format(idx), 'wb')      # binary mode is important
    # # w = png.Writer(img.shape[1], img.shape[0], greyscale=True)
    # # w.write(f, img)
    # # f.close()
    #
    # return

# if __name__ == '__main__':
#     p = '/home/aimenext/nhinhlt/dataset/spam_end_epoch.csv'
#     best_path = '/home/ubuntu/nhinhlt/test3/image-detection/auto_train_crnn/checkpoint/20200506_042514/1/1_weights.2008-1.192.hdf5'
#     df_training = pd.read_csv(p)
#     # print(df_training)
#     for index, line in df_training.iterrows():
#         # print('line', line)
#         if line['fullPath']==best_path:
#             # print('line',line)
#             print('line',dict(line))