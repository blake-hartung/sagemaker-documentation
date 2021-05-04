from tensorflow.keras import Sequential
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import Model, Input
from tensorflow.keras.layers import LSTM, Embedding, Dense, Dropout, SpatialDropout1D
import time
import pickle
import pandas as pd
import numpy as np
import os
import argparse
pd.options.mode.chained_assignment = None

def main(args):
    training_data = pd.read_csv(os.path.join(args.data_dir, "Keras_latest_training_data.csv"))

    # Version control
    model_trained_time = time.strftime("%Y%m%d-%H%M")
    model_version = 'model_' + model_trained_time

    # Intent training begins
    traindata = training_data[['text','intent']]
    traindata = traindata[pd.notna(traindata['text'].values)]

    # Randomly sample 5% of validation
    validation_splitrate =  0.05
    traindata_validation = traindata.sample(frac=validation_splitrate)
    traindata_train = traindata.loc[~traindata.index.isin(traindata_validation.index)]
    # reshape the traindate as first 95% train, last 5% validation
    traindata = pd.concat([traindata_train, traindata_validation ])

    # tokenizer
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(traindata['text'].values)
    X = tokenizer.texts_to_sequences(traindata['text'].values)
    X = pad_sequences(X, maxlen = 50)

    # Y labels
    Ylabel = np.array(sorted(set(traindata['intent'])))
    Y = pd.get_dummies(traindata['intent'], prefix='', prefix_sep='')
    Y = Y.T.reindex(Ylabel).T.fillna(0).values

    intent_tokens ={"X": X,
                    "Y": Y,
                    "Ylabel": Ylabel,
                    "tokenizer": tokenizer}

    with open('{}/{}_intent_tokens.pickle'.format(args.model_dir, model_version), 'wb') as handle:
        pickle.dump(intent_tokens, handle, protocol=pickle.HIGHEST_PROTOCOL)

    ## parameters
    max_features = np.max(X)
    Ndense = len(set(traindata['intent']))

    # LSTM train
    model = Sequential()
    model.add(Embedding(max_features+1, args.embed_dim, input_length=X.shape[1]))
    model.add(SpatialDropout1D(args.sdropoutrate))
    model.add(LSTM(args.lstm_out, dropout=args.dropoutrate, recurrent_dropout=args.rdropoutrate))
    model.add(Dense(Ndense,activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    intent_history = model.fit(X, Y, epochs=5, validation_split=validation_splitrate, batch_size=args.batch_size, verbose=2)

    # Saving intent model
    intent_history.model.save('{}/LSTM_history.h5'.format(args.model_dir), save_format='h5')

if __name__ == "__main__":
    try:
        model_dir_default = os.environ['SM_MODEL_DIR']
    except KeyError:
        model_dir_default = "/opt/ml/model"
    try:
        training_dir_default = os.environ['SM_CHANNEL_TRAINING']
    except KeyError:
        training_dir_default = "/opt/ml/input/data/training"
    parser = argparse.ArgumentParser()
    parser.add_argument('--embed-dim', type=int, default=512)
    parser.add_argument('--lstm-out', type=int, default=196)
    parser.add_argument('--sdropoutrate', type=float, default=0.3)
    parser.add_argument('--dropoutrate', type=float, default=0.2)
    parser.add_argument('--rdropoutrate', type=float, default=0.2)
    parser.add_argument('--batch-size', type=int, default=128)
    # Env variables
    parser.add_argument('train')
    parser.add_argument('--model-dir', type=str, default=model_dir_default)
    parser.add_argument('--data-dir', type=str, default=training_dir_default)

    main(parser.parse_args())