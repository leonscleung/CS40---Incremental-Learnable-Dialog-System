from src.readers import SkipGramDatasetReader, Seq2SeqDatasetReader
from src.models import SkipGramModel, Seq2SeqModel
from src.constants import *
import tensorflow as tf
from src.utilities import FileUtility


def initialize():

    # download models from google drive first
    tf.reset_default_graph()
    session = tf.Session()

    # resume previously saved word dict
    word_dict = SkipGramDatasetReader.resume_word_dict(WORD_DICT_Q_PATH)
    wv_model = SkipGramModel(session=session, word_dict=word_dict, voc_size=VOCAB_SIZE, embedding_size=EMBEDDING_SIZE,
                             sample_size=SAMPLE_SIZE)
    wv_model.load_model(WV_MODEL_PATH)

    # recorded from training, max length of question for all
    # resume word dict for answers (one hot lookup)
    # change the load_model to train the model
    # self, total_samples, dataset_iterator, validate_iterator,
    # num_epoch=5000, display_interval=50
    word_dict_a = Seq2SeqDatasetReader.resume_answer_dict()
    seq2seq_models = Seq2SeqModel(session=session, word_dict_a=word_dict_a,max_len_q=MAX_LEN_Q,
                                  embedding_size=wv_model.embedding_size, hidden_size=HIDDEN_SIZE)
    seq2seq_models.load_model(SEQ_MODEL_PATH)

    return seq2seq_models, wv_model


def initTrain():
    # training
    FileUtility.mkdir(FILES_ROOT)
    FileUtility.mkdir(WV_MODEL_ROOT)
    FileUtility.mkdir(WORD_DICT_ROOT)
    FileUtility.mkdir(SEQ_MODEL_ROOT)

    tf.reset_default_graph()
    with tf.Session() as session:
        # prepare Word2Vec-skipgram dataset
        dataset = SkipGramDatasetReader(
            word_dict_path=WORD_DICT_Q_PATH, window_size=WINDOW_SIZE)
        wv_model = SkipGramModel(
            session=session, word_dict=dataset.word_dict,
            voc_size=dataset.vocab_size, embedding_size=EMBEDDING_SIZE,
            sample_size=SAMPLE_SIZE2, lr=LEARNING_RATE)
        total_batch = dataset.num_samples // BATCH_SIZE
        dataset_iterator = dataset.prepare(
            num_epoch=NUM_EPOCH, batch_size=BATCH_SIZE, shuffle=True)
        wv_model.train(num_epoch=NUM_EPOCH, total_batch=total_batch,
                       dataset_iterator=dataset_iterator,
                       display_interval=DISPLAY_INTERVAL)
        wv_model.save_model(WV_MODEL_PATH)

    tf.reset_default_graph()
    with tf.Session() as session:
        # resume previously saved worddict
        word_dict = SkipGramDatasetReader.resume_word_dict(WORD_DICT_Q_PATH)
        wv_model = SkipGramModel(session=session, word_dict=word_dict, voc_size=VOCAB_SIZE,
                                 embedding_size=EMBEDDING_SIZE, sample_size=SAMPLE_SIZE2)
        wv_model.load_model(WV_MODEL_PATH)

        # prepareSeq2Seqtrainingdataset
        datasets = Seq2SeqDatasetReader(
            word_dict_a_path=WORD_DICT_A_PATH, wv_model=wv_model)
        dataset_iterators = datasets.prepare(
            batch_size=BATCH_SIZE, num_epoch=NUM_EPOCH2, shuffle=True)
        validate_iterators = datasets.prepare(
            batch_size=128, num_epoch=-1, shuffle=False)
        seq2seq_models = Seq2SeqModel(
            session, word_dict_a=datasets.word_dict_a,
            max_len_q=datasets.max_len_q,
            embedding_size=wv_model.embedding_size,
            hidden_size=HIDDEN_SIZE, lr=LEARNING_RATE)
        seq2seq_models.train(
            num_epoch=NUM_EPOCH2, total_samples=datasets.num_seq,
            dataset_iterator=dataset_iterators,
            validate_iterator=validate_iterators,
            display_interval=DISPLAY_INTERVAL)
        seq2seq_models.save_model(SEQ_MODEL_PATH)
