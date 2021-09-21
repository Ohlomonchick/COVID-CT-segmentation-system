import torch
import numpy as np
import os
# import matplotlib.pyplot as plt
import albumentations
import cv2
from PIL import Image
from torchvision import transforms


class Segmentation():
    def __init__(self, image, path_to_model):
        self.image = image
        self.path_to_model = path_to_model

    def preprocess_image(self, image_arr, mean_std=None):
        image_arr[image_arr > 500] = 500
        image_arr[image_arr < -1500] = -1500
        min_perc, max_perc = np.percentile(image_arr, 5), np.percentile(image_arr, 95)
        image_arr_valid = image_arr[(image_arr > min_perc) & (image_arr < max_perc)]
        mean, std = (image_arr_valid.mean(), image_arr_valid.std()) if mean_std is None else mean_std
        image_arr = (image_arr - mean) / std
        # print(f'mean {mean}, std {std}')
        return image_arr, (mean, std)

    def mask_to_onehot(self, mask, palette):
        """
        Converts a segmentation mask (H, W, C) to (H, W, K) where the last dim is a one
        hot encoding vector, C is usually 1 or 3, and K is the number of class.
        """
        semantic_map = []
        for colour in palette:
            equality = np.equal(mask, colour)
            class_map = np.all(equality, axis=-1)
            semantic_map.append(class_map)
        semantic_map = np.stack(semantic_map, axis=-1).astype(np.float32)
        return torch.from_numpy(semantic_map)

    def draw_masks(self, orig_im, mask, color1=[255, 255, 0], color2=[255, 0, 0]):
        # lung = np.uint8(orig_im)
        lung = cv2.cvtColor(orig_im, cv2.COLOR_GRAY2BGR)
        mask_glass = np.uint8(mask[:, :, 0] * 255)
        mask_consolidation = np.uint8(mask[:, :, 1] * 255)

        color1 = np.array(color1, dtype='uint8')
        color2 = np.array(color2, dtype='uint8')

        masked_glass = np.where(mask_glass[..., None], color1, lung)
        out = np.where(mask_consolidation[..., None], color2, masked_glass)
        return out

    def calc_lesion(self, mask, channel):
        percentage = 0
        # mask shape should be : Batch_Size x Height x Width x Channels
        pixels_class = cv2.countNonZero(np.float32(mask[:, :, channel]))
        total = mask.shape[1] * mask.shape[1]
        pixels_lungs = total - cv2.countNonZero(np.float32(mask[:, :, 3]))

        percentage = round(pixels_class / pixels_lungs * 100)

        title = ''
        if channel == 0:
            title = 'ground glass'
        if channel == 1:
            title = 'consolidation'
        return percentage, title

    @staticmethod
    def put_masks(orig_im, semantic_map, channels=[], colors=[], only_mask=False):

        # len(channels) must equal len(colors)
        # in channels: 0 - ground glass, 1 - consolidation, 2 - lung other, 3 - background

        assert len(channels) == len(colors)

        if not only_mask:
            image = cv2.cvtColor(orig_im, cv2.COLOR_GRAY2BGR)
        else:
            mask = np.uint8(semantic_map[:, :, 0:1])
            # new_image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            image = mask

        for i in range(len(channels)):
            mask = np.uint8(semantic_map[:, :, channels[i]] * 255)
            color = np.array(colors[i], dtype='uint8')
            image = np.where(mask[..., None], color, image)

        return image

    def predict_cat(self, gr_glass, consolidation):
        if (consolidation == 0 and gr_glass == 0):
            return 0
        elif (consolidation == 0 and gr_glass < 25):
            return 1
        elif (consolidation == 0 and gr_glass >= 25 and gr_glass < 50):
            return 2
        elif (consolidation > 0 and (consolidation + gr_glass) < 75):
            return 3
        elif ((consolidation + gr_glass) >= 75):
            return 4

    def main(self):
        # device = torch.cuda.set_device(0)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model = torch.load(self.path_to_model)
        model = model.to(device)
        model.eval()

        # обработка
        image_processed, (mean, std) = self.preprocess_image(self.image)
        tfms = transforms.Compose([
            transforms.ToPILImage(),
            # transforms.Resize(256),
            transforms.ToTensor(),
            transforms.Normalize([0.485], [0.229])])

        img_tensor = tfms(image_processed).to(device).unsqueeze(0)
        # предсказание
        with torch.no_grad():
            output = model(img_tensor)

            mask_pred = torch.argmax(output, dim=1).cpu()
            # mask_pred = np.asarray(mask_pred.to('cpu'), dtype=np.uint8) / 255
            mask_pred = mask_pred.squeeze(0)

        # сделать 4 канала
        palette = [[0], [1], [2], [3]]
        semantic_map = self.mask_to_onehot(torch.unsqueeze(mask_pred, -1).numpy(), palette)

        # посчитать процент поражения
        percentage1, title1 = self.calc_lesion(semantic_map, 0)
        percentage2, title2 = self.calc_lesion(semantic_map, 1)

        # предсказание класса
        category = self.predict_cat(percentage1, percentage2)

        # визуализация
        # out = self.draw_masks(self.image, semantic_map)
        out = self.put_masks(self.image, semantic_map, [0, 2], [[255, 255, 0], [0, 0, 255]])

        return (percentage1, title1), (percentage2, title2), out, category, semantic_map, self.image


def get_color_transp_ims(orig_im, semantic_map, channels=[], colors=[]):

  assert len(channels) == len(colors)

  images = []
  for i in range(len(channels)):
    result = cv2.cvtColor(orig_im, cv2.COLOR_BGR2RGBA)
    binary = semantic_map[..., channels[i]]
    color = colors[i]
    result[:, :, 0] = binary * color[0]
    result[:, :, 1] = binary * color[1]
    result[:, :, 2] = binary * color[2]
    result[:, :, 3] = binary * color[3]

    # trans_mask = result[:, :, 3] == 0
    # result[trans_mask] = [255, 255, 255, 255]
    # tmp = cv2.cvtColor(result, cv2.COLOR_BGRA2BGR)
    # V = cv2.cvtColor(tmp, cv2.COLOR_BGR2HSV)[..., 2]
    # _, A = cv2.threshold(V, 100, 255, cv2.THRESH_BINARY_INV)
    # result = np.dstack((tmp, A))

    images.append(result)

  return images


