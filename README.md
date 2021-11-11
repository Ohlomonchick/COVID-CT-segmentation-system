# 42-EPOCHS
 A neural network able to segment lung damage

Overview
***ENGLISH***


We present a model which is able to segment areas of ground glass and consolidation and determine the severity of the illness (from CT-0 for being healthy to CT-4 for the most severe stage) on CT scans of COVID-19 patients. 


Data


In this project we used data from different sources (3 datasets overall). The first two are datasets provided by Radiopedia and MedSeg containing 829 and 100 images respectively. They were taken from this Kaggle competition:https://www.kaggle.com/c/covid-segmentation .The third dataset is from Mosmed (https://mosmed.ai/datasets/covid19_1110/) containing 1110 separate sets of images, but only 50 of them has labels (only ground glass and consolidation, but we need 4 classes for our model). Because of this we have made about 30 masks ourselves with the help of a radiologist.


Model


As a model we used ensemble consisting of a pretrained UNet model with backbone "EfficientNet-b0" and pretrained PSPNet with backbone “EfficientNet-b2” , trained for about an hour on 7 epochs. Loss function is CrossEntropy. Our mean IoU score is 0.744 and accuracy is 0.94.


Results


Example:
Original and segmented images (yellow stands for ground glass and red for consolidation)
     


Model predicts 4 classes: 0 - ground glass, 1 - consolidation, 2 - lungs other, 3 - background.  Output is a segmented image with two main classes which are lung damage.

Visualisation


We presented our results as a web environment where you can load a CT scan (512 x 512 pixels) or an archive and get a segmented image. The time it takes to perform segmentation on 1 image is between 2 and 20 seconds depending on the PC's power . You can easily switch between different classes and also download the result image or archive.


How to run
1. Clone GitHub repository by the link below
2. Install required libraries from requirements.txt с using command **pip install -r requirements.txt**
3. Go to 42 EPOCHS\\\_42epochs_ folder
4. Run **python manage.py runserver** from that folder
5. Follow the link which appeared in the terminal
  





Useful links


Our GitHub repository:https://github.com/Ohlomonchick/42-EPOCHS

Our GoogleColab notebook: https://colab.research.google.com/drive/1pcZDE0qGj8uooFNYziMvP4p5vL61pMyM?usp=sharing


***RUSSIAN***

Мы представляем модель, которая может сегментировать участки матового стекла и консолидации, а также определять тяжесть заболевания ( от КТ-0 для здорового человека до КТ-4 для наиболее тяжелой стадии заболевания) на компьютерной томографии COVID. -19 пациентов.


Данные
В этом проекте мы использовали данные из разных источников (всего 3 набора данных). Первые два - это наборы данных, предоставленные Radiopedia и MedSeg, содержащие 829 и 100 изображений соответственно. Они были взяты из конкурса Kaggle: https://www.kaggle.com/c/covid-segmentation. Третий набор данных взят из Mosmed (https://mosmed.ai/datasets/covid19_1110/) и содержит 1110 отдельных наборов изображений,, но только небольшая часть из них имеет маски. Из-за этого мы сами сделали маски в сотрудничестве с рентгенологом.




**Модель**
В качестве модели мы использовали ансамбль, состоящий из предобученной модели UNet с backbone «EfficientNet-b0» и предобученной модели PSPNet с backbone “EfficientNet-b2”, обученную чуть больше часа на 7 эпохах. Функция потерь - CrossEntropy. Метрика mean IoU составляет 0.744, а точность - 0.94.


Результаты
Пример:
Исходное и сегментированное изображения (желтое - матовое стекло, красное - консолидация)
     
Модель предсказывает 4 класса: 0 - матовое стекло, 1 - консолидация, 2 - оставшиеся легкие, 3 - фон. Модель выводит картинку только с двумя основными классами - поражениями легких.
  

Визуализация
Мы представили наши результаты в виде веб-страницы, в которую вы можете загрузить компьютерную томографию (512 x 512 пикселей) и получить сегментированное изображение. Время, необходимое для выполнения сегментации, составляет 2-20 секунд в зависимости от мощности ПК. Вы можете легко переключаться между разными классами, а также загрузить изображение результата.


Инструкция по запуску
1. Отклонироваться от GitHub репозитория по ссылке ниже
2. Установить необходимые библиотеки из файла requirements.txt с помощью команды **pip install -r requirements.txt**
3. Перейти в папку 42 EPOCHS\\\_42epochs_
4. Запустить из неё команду **python manage.py runserver**
5. Перейти по ссылке, которая появится в консоли
  







Полезные ссылки
Наш репозиторий GitHub: https://github.com/Ohlomonchick/42-EPOCHS
Копия нашего GoogleColab ноутбука: https://colab.research.google.com/drive/1pcZDE0qGj8uooFNYziMvP4p5vL61pMyM?usp=sharing