# 42-EPOCHS
 A neural network able to segment lung damage

As a part of the competition we present a model which is able to segment areas of ground glass and consolidation and determine the severity of the illness (from CT-0 for being healthy to CT-4 for the most severe stage) on CT scans of COVID-19 patients. 

Data

In this project we used data from different sources (3 datasets overall). The first two are datasets provided by Radiopedia and MedSeg containing 829 and 100 images respectively. They were taken from this Kaggle competition:https://www.kaggle.com/c/covid-segmentation .The third dataset is from Mosmed (https://mosmed.ai/datasets/covid19\_1110/) containing 1110 separate sets of images, but only 50 of them has labels (only ground glass and consolidation, but we need 4 classes for our model). Because of this we have made about 200 masks ourselves with the help of a radiologist.

Model

As a model we used UNet architecture with a backbone "EfficientNet-b0", trained for about an \_\_\_ on \_\_\_ epochs. Loss function is CrossEntropy.. Our IoU score is 0.65 and accuracy is 0.97.

Results

Example:

Original and segmented images (yellow stands for ground glass and red for consolidation)



Model predicts 4 classes: 0 - ground glass, 1 - consolidation, 2 - lungs other, 3 - background.  Output is a segmented image with two main classes which are lung damage.



We presented our results as a web environment where you can load a CT scan (512 x 512 pixels) and get a segmented image. The time it takes to perform segmentation is about 40 seconds. You can easily switch between different classes and also download the result image.

Video of the process:


Useful links

Competition website: https://aiijc.com/ru/

Our GitHub repository:https://github.com/Ohlomonchick/42-EPOCHS

Our website:



НА РУССКОМ (RUSSIAN)

Обзор

В рамках конкурса мы представляем модель, которая может сегментировать участки матового стекла и консолидации, а также определять тяжесть заболевания ( от КТ-0 для здорового человека до КТ-4 для наиболее тяжелой стадии заболевания) на компьютерной томографии COVID. -19 пациентов.

Данные

В этом проекте мы использовали данные из разных источников (всего 3 набора данных). Первые два - это наборы данных, предоставленные Radiopedia и MedSeg, содержащие 829 и 100 изображений соответственно. Они были взяты из конкурса Kaggle: https://www.kaggle.com/c/covid-segmentation. Третий набор данных взят из Mosmed (https://mosmed.ai/datasets/covid19\_1110/) и содержит 1110 отдельных наборов изображений,, но только небольшая часть из них имеет маски. Из-за этого мы сами сделали около 200 масок с помощью рентгенолога.

Модель

В качестве модели мы использовали архитектуру UNet с backbone «EfficientNet-b0», обученную примерно \_\_\_ на \_\_\_ эпохах. Функция потерь - CrossEntropy. Метрика IoU составляет 0,65, а точность - 0,97.

Результаты

Пример:

Исходное и сегментированное изображения (желтое - матовое стекло, красное - консолидация)



Модель предсказывает 4 класса: 0 - матовое стекло, 1 - консолидация, 2 - оставшиеся легкие, 3 - фон. Модель выводит картинку только с двумя основными классами - поражениями легких.

Маски

Матовое стекло и консолидация:
