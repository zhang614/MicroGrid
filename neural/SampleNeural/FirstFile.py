import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras

layers=keras.layers
print("tensorflow version",tf.__version__)
data=pd.read_csv("wine_data.csv")

#shuffle data
data=data.sample(frac=1)
#removes data where country is null
data=data[pd.notnull(data['country'])]
data=data[pd.notnull(data['price'])]
#remove first column axis
data=data.drop(data.columns[0],axis=1)

variety_threshold=500
value_counts=data['variety'].value_counts()
print(value_counts,"value_counts")
to_remove=value_counts[value_counts<=variety_threshold].index
print(to_remove,"to_remove")
data.replace(to_remove,np.nan,inplace=True)
data=data[pd.notnull(data['variety'])]
value_counts2=data['variety'].value_counts()
print(len(value_counts2))

train_size=int(len(data)*0.8)

#Train based on following features
description_Train=data['description'][:train_size]
variety_train=data['variety'][:train_size]

#TrainLabels
labels_train=data['price'][:train_size]

#Train based on following features
description_Test=data['description'][train_size:]
variety_Test=data['variety'][train_size:]

#TrainLabels
labels_Test=data['price'][train_size:]

#as we cannot directly feed description we need to convert that into a sequence of 0's and 1's
vocab_size=12000
tokenize=keras.preprocessing.text.Tokenizer(num_words=vocab_size,char_level=False)
tokenize.fit_on_texts(description_Train)

description_bow_Train=tokenize.texts_to_matrix(description_Train)
description_bow_Test=tokenize.texts_to_matrix(description_Test)

encoder=LabelEncoder()
encoder.fit(variety_train)
variety_train=encoder.transform(variety_train)
variety_Test=encoder.transform(variety_Test)
num_classes=np.max(variety_train)+1


variety_train=keras.utils.to_categorical(variety_train,num_classes)
variety_test=keras.utils.to_categorical(variety_Test,num_classes)
print(variety_train,"variety_train")


#building model
bow_inputs=layers.Input(shape=(vocab_size,))
print(bow_inputs,"bow_inputs")
variety_inputs=layers.Input(shape=(num_classes,))
mergedLayer=layers.concatenate([bow_inputs,variety_inputs])#merging inputs
mergedLayer=layers.Dense(256,activation='relu')(mergedLayer)#adding activation function
predictions=layers.Dense(1)(mergedLayer)
wide_model=keras.Model(inputs=[bow_inputs,variety_inputs],outputs=predictions)

wide_model.compile(loss='mse',optimizer='adam',metrics=['accuracy'])
print(wide_model.summary())


#adding deepmodel feature
train_embeded=tokenize.texts_to_sequences(description_Train)
test_embeded=tokenize.texts_to_sequences(description_Test)

maxseqlength=170
train_embeded=keras.preprocessing.sequence.pad_sequences(train_embeded,maxlen=maxseqlength,padding='post')
test_embeded=keras.preprocessing.sequence.pad_sequences(test_embeded,maxlen=maxseqlength,padding='post')

deep_inputs=layers.Input(shape=(maxseqlength,))
embedding=layers.Embedding(vocab_size,8,input_length=maxseqlength)(deep_inputs)
embedding=layers.Flatten()(embedding)
embededout=layers.Dense(1)(embedding)
deep_model=keras.Model(inputs=deep_inputs,outputs=embededout)
print(deep_model.summary())


deep_model.compile(loss='mse',optimizer='adam',metrics=['accuracy'])

#combining wide and deep into one model
merged_out=layers.concatenate([wide_model.output,deep_model.output])
merged_out=layers.Dense(1)(merged_out)
combinedModel=keras.Model(wide_model.input+[deep_model.input],merged_out)
print(combinedModel.summary())

combinedModel.compile(loss='mse',optimizer='adam',metrics=['accuracy'])

combinedModel.fit([description_bow_Train,variety_train]+[train_embeded],labels_train,epochs=8,batch_size=128)

#now evaluating
combinedModel.evaluate([description_bow_Test,variety_test]+[test_embeded],labels_Test,batch_size=128)

predictions=combinedModel.predict([description_bow_Test,variety_test]+[test_embeded])

num_prediction=40
diff=0
for i in range(num_prediction):
    val=predictions[i]
    print(description_Test.iloc[i])
    print('Predicted:',val[0],'Actual:',labels_Test.iloc[i],'\n')
    diff+=abs(val[0]-labels_Test.iloc[i])

print('Average Prediction Difference:',diff/num_prediction)