# -*- coding: utf-8 -*-
"""MetinAvcısı.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GFb3yPd0pWDq1tXmnvQrWVwQWER1E5GW

Görüntü işleme ,aritmetik hesaplama ve verileri görselleştirme gibi işlemler için gerekli kütüphaneleri ekliyoruz.
"""

import pandas as pd
import numpy as np

from glob import glob
from tqdm.notebook import tqdm

import matplotlib.pyplot as plt
from PIL import Image

plt.style.use('ggplot')

!apt-get install tesseract-ocr

"""Bir metin ayıklama yazılımı olan **Tesseract**'ın kurulumu"""

!pip install pytesseract

"""annot.parquet görüntü metin etiketlemeleri içindir, dataset içindeki annot.csv dosyasıyla aynı bilgileri içerir.

img.parquet ise görüntülerin meta verisine sahiptir. dataset'deki img.csv ile aynı, ancak Parquet formatında.
"""

annot = pd.read_parquet('/content/drive/MyDrive/text detection/annot.parquet')
imgs = pd.read_parquet('/content/drive/MyDrive/text detection/img.parquet')
img_fns = glob('/content/drive/MyDrive/text detection/train_images/*')

"""Görüntü görselleştirme:"""

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(plt.imread(img_fns[0]))
ax.axis('off')
plt.show()

"""Metin etiketinin ID'si ,resim ID'si, utf8_string gibi bize metin ayıklamada yardımcı olabilecek imgeye ait bilgileri verir."""

image_id = img_fns[0].split('/')[-1].split('.')[0]
annot.query('image_id == @image_id')

"""Verisetinden seçilen 25 resim aynı düzlem üzerinden görselleştirilir"""

fig, axs = plt.subplots(5, 5, figsize=(20, 20))
axs = axs.flatten()
for i in range(25):
    axs[i].imshow(plt.imread(img_fns[i]))
    axs[i].axis('off')
    image_id = img_fns[i].split('/')[-1].rstrip('.jpg')
    n_annot = len(annot.query('image_id == @image_id'))
    axs[i].set_title(f'{image_id} - {n_annot}')
plt.show()

"""Tesseract OCR nin Phyton ile kullanılması için arayüz sağlanır, metin ayıklamada kullanılacak olan dil İngilizce olarak ayarlanır."""

import pytesseract

print(pytesseract.image_to_string(img_fns[11], lang='eng'))

"""Seçilen resimlerden indexi 11 olan,yani 12. resmi görüntüler,eksen çizgileri kaldırılır."""

fig, ax = plt.subplots(figsize=(10,10))
ax.imshow(plt.imread(img_fns[11]))
ax.axis('off')
plt.show()

"""Keras OCR yüklenir:"""

!pip install keras-ocr -q

"""Keras içe aktarılır ve pipeline adında metin tanımlama bileşenlerini içeren bir yapı oluşturulur."""

import keras_ocr
pipeline = keras_ocr.pipeline.Pipeline()

"""Seçilen 12. resmin metin tanımlamaları yapılır ve metinler konumlarıyla birlikte results değişkenine aktarılır."""

results = pipeline.recognize([img_fns[11]])

"""Eldeki metin ve konum bilgileri Pandas Dataframe ile tablo haline getirilir."""

pd.DataFrame(results[0], columns=['text', 'bbox'])

"""Elde edilen tanımlamalar ilgili resim üzerinde görselleştirilir."""

fig, ax = plt.subplots(figsize=(10, 10))
keras_ocr.tools.drawAnnotations(plt.imread(img_fns[11]), results[0], ax=ax)
ax.set_title('Keras OCR Result Example')
plt.show()

"""25 resim sırayla işlenir."""

pipeline = keras_ocr.pipeline.Pipeline()

dfs = []
for img in tqdm(img_fns[:25]):
    results = pipeline.recognize([img])
    result = results[0]
    img_id = img.split('/')[-1].split('.')[0]
    img_df = pd.DataFrame(result, columns=['text', 'bbox'])
    img_df['img_id'] = img_id
    dfs.append(img_df)
kerasocr_df = pd.concat(dfs)

"""Belirli bir görüntü üzerinde Keras OCR tarafından yapılan metin tanıma sonuçlarını ve bu sonuçları görsel olarak karşılaştırmak için tasarlanmış bir fonksiyon içerir."""

def plot_compare(img_fn, kerasocr_df):
    img_id = img_fn.split('/')[-1].split('.')[0]
    fig, axs = plt.subplots(1, 1, figsize=(15, 10))

    keras_results = kerasocr_df.query('img_id == @img_id')[['text','bbox']].values.tolist()
    keras_results = [(x[0], np.array(x[1])) for x in keras_results]
    keras_ocr.tools.drawAnnotations(plt.imread(img_fn),
                                    keras_results, ax=axs)
    axs.set_title('keras_ocr results', fontsize=24)
    plt.show()

"""İlgili 25 resmin Keras OCR sonuçları karşılaştırılır."""

# Loop over results
for img_fn in img_fns[:25]:
    plot_compare(img_fn, kerasocr_df)