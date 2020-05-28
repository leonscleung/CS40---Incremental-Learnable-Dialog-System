# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 16:23:37 2016

@author: Bing Liu (liubing@cmu.edu)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time
import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

from nlu import multi_task_model, data_utils

import subprocess
import stat
import os
import pathlib

root = pathlib.Path(os.path.abspath(__file__)).parent.parent
data_path = str(root) + '/data/ATIS_samples'
training_path = str(root) + '/model_tmp'
# tf.app.flags.DEFINE_float("learning_rate", 0.1, "Learning rate.")
#tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.9,
#                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 64,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 128, "Size of each model layer.")
tf.app.flags.DEFINE_integer("word_embedding_size", 128 , "word embedding size")
tf.app.flags.DEFINE_integer("num_layers", 1, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("in_vocab_size", 10000, "max vocab Size.")
tf.app.flags.DEFINE_integer("out_vocab_size", 10000, "max tag vocab Size.")
tf.app.flags.DEFINE_string("data_dir", data_path, "Data directory")
tf.app.flags.DEFINE_string("model_dir", training_path, "Training directory.")
tf.app.flags.DEFINE_string("task", "tagging", "Options: joint; intent; tagging")
tf.app.flags.DEFINE_integer("max_train_data_size", 0,
                            "Limit on the size of training data (0: no limit)")
tf.app.flags.DEFINE_integer("steps_per_checkpoint", 100,
                            "How many training steps to do per checkpoint.")
tf.app.flags.DEFINE_integer("max_training_steps", 10000,
                            "Max training steps.")
tf.app.flags.DEFINE_integer("max_test_data_size", 0,
                            "Max size of test set.")
tf.app.flags.DEFINE_boolean("use_attention", True,
                            "Use attention based RNN")
tf.app.flags.DEFINE_integer("max_sequence_length", 50,
                            "Max sequence length.")
tf.app.flags.DEFINE_float("dropout_keep_prob", 0.2,
                          "dropout keep cell input and output prob.")  
tf.app.flags.DEFINE_boolean("bidirectional_rnn", True,
                            "Use birectional RNN")

FLAGS = tf.app.flags.FLAGS

print(FLAGS.data_dir)

if FLAGS.max_sequence_length == 0:
    print ('Please indicate max sequence length. Exit')
    exit()

if FLAGS.task is None:
    print ('Please indicate task to run.' + 
           'Available options: intent; tagging; joint')
    exit()

task = dict({'intent':0, 'tagging':0, 'joint':0})
if FLAGS.task == 'intent':
    task['intent'] = 1
elif FLAGS.task == 'tagging':
    task['tagging'] = 1
elif FLAGS.task == 'joint':
    task['intent'] = 1
    task['tagging'] = 1
    task['joint'] = 1
    
_buckets = [(FLAGS.max_sequence_length, FLAGS.max_sequence_length)]
# _buckets = [(3, 10), (10, 25)]

# metrics function using conlleval.pl
def conlleval(p, g, w, filename):
    '''
    INPUT:
    p :: predictions
    g :: groundtruth
    w :: corresponding words

    OUTPUT:
    filename :: name of the file where the predictions
    are written. it will be the input of conlleval.pl script
    for computing the performance in terms of precision
    recall and f1 score
    '''
    out = ''
    for sl, sp, sw in zip(g, p, w):
        # out += '\n'
        for wl, wp, w in zip(sl, sp, sw):
            out += w + ' ' + wl + ' ' + wp + '\n'
        out += '\n\n'

    f = open(filename, 'w')
    f.writelines(out[:-1]) # remove the ending \n on last line
    f.close()

    return get_perf(filename)


def conlleval_test(p, w, filename):
    '''
    INPUT:
    p :: predictions
    w :: corresponding words

    OUTPUT:
    filename :: name of the file where the predictions
    are written. it will be the input of conlleval.pl script
    for computing the performance in terms of precision
    recall and f1 score
    '''
    out = ''
    for sp, sw in zip(p, w):
        # out += '\n'
        for wp, w in zip(sp, sw):
            out += w + ' ' + wp + '\n'
        out += '\n\n'

    f = open(filename, 'w')
    f.writelines(out[:-1]) # remove the ending \n on last line
    f.close()
    return filename

def get_perf(filename):
    ''' run conlleval.pl perl script to obtain
    precision/recall and F1 score '''
    out = ''
    _conlleval = os.path.dirname(os.path.realpath(__file__)) + '/conlleval.pl'
    os.chmod(_conlleval, stat.S_IRWXU)  # give the execute permissions
    # print(_conlleval)
    perl = "/usr/bin/perl"
    proc = subprocess.Popen([perl, _conlleval],
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            encoding='utf8')

    stdout, _ = proc.communicate(''.join(open(filename).readlines()))
    for line in stdout.split('\n'):
        # print(line)
        if 'accuracy' in line:
            # print(line.split())
            out = line.split()
            break
    print(out[6][:-2])
    precision = float(out[6][:-2])
    recall = float(out[8][:-2])
    f1score = float(out[10])

    return {'p': precision, 'r': recall, 'f1': f1score}



def read_data(source_path, target_path, label_path, max_size=None):
  """Read data from source and target files and put into buckets.
  Args:
    source_path: path to the files with token-ids for the word sequence.
    target_path: path to the file with token-ids for the tag sequence;
      it must be aligned with the source file: n-th line contains the desired
      output for n-th line from the source_path.
    label_path: path to the file with token-ids for the intent label
    max_size: maximum number of lines to read, all other will be ignored;
      if 0 or None, data files will be read completely (no limit).
  Returns:
    data_set: a list of length len(_buckets); data_set[n] contains a list of
      (source, target, label) tuple read from the provided data files that fit
      into the n-th bucket, i.e., such that len(source) < _buckets[n][0] and
      len(target) < _buckets[n][1];source, target, label are lists of token-ids
  """
  data_set = [[] for _ in _buckets]
  with tf.gfile.GFile(source_path, mode="r") as source_file:
    with tf.gfile.GFile(target_path, mode="r") as target_file:
      with tf.gfile.GFile(label_path, mode="r") as label_file:
        source = source_file.readline()
        target = target_file.readline()
        label = label_file.readline()
        counter = 0
        while source and target and label and (not max_size \
                                               or counter < max_size):
          counter += 1
          if counter % 100000 == 0:
            print("  reading data line %d" % counter)
            sys.stdout.flush()
          source_ids = [int(x) for x in source.split()]
          target_ids = [int(x) for x in target.split()]
          label_ids = [int(x) for x in label.split()]
#          target_ids.append(data_utils.EOS_ID)
          for bucket_id, (source_size, target_size) in enumerate(_buckets):
            if len(source_ids) < source_size and len(target_ids) < target_size:
              data_set[bucket_id].append([source_ids, target_ids, label_ids])
              break
          source = source_file.readline()
          target = target_file.readline()
          label = label_file.readline()
  return data_set # 3 outputs in each unit: source_ids, target_ids, label_ids


def read_data_test(source_path, target_path, label_path, max_size=None):
  """Read data from source and target files and put into buckets.
  Args:
    source_path: path to the files with token-ids for the word sequence.
    target_path: path to the file with token-ids for the tag sequence;
      it must be aligned with the source file: n-th line contains the desired
      output for n-th line from the source_path.
    label_path: path to the file with token-ids for the intent label
    max_size: maximum number of lines to read, all other will be ignored;
      if 0 or None, data files will be read completely (no limit).
  Returns:
    data_set: a list of length len(_buckets); data_set[n] contains a list of
      (source, target, label) tuple read from the provided data files that fit
      into the n-th bucket, i.e., such that len(source) < _buckets[n][0] and
      len(target) < _buckets[n][1];source, target, label are lists of token-ids
  """
  data_set = [[] for _ in _buckets]
  with tf.gfile.GFile(source_path, mode="r") as source_file:
    with tf.gfile.GFile(target_path, mode="r") as target_file:
      with tf.gfile.GFile(label_path, mode="r") as label_file:
        source = source_file.readline()
        target = target_file.readline()
        label = label_file.readline()
        counter = 0
        while source and (not max_size or counter < max_size):
          counter += 1
          if counter % 100000 == 0:
            print("  reading data line %d" % counter)
            sys.stdout.flush()
          source_ids = [int(x) for x in source.split()]
          target_ids = [int(x) for x in target.split()]
          label_ids = [int(x) for x in label.split()]
    #          target_ids.append(data_utils.EOS_ID)
          for bucket_id, (source_size, target_size) in enumerate(_buckets):
            if len(source_ids) < source_size:
              data_set[bucket_id].append([source_ids, target_ids, label_ids])
              break
          source = source_file.readline()
          target = target_file.readline()
          label = label_file.readline()
  return data_set # 3 outputs in each unit: source_ids, target_ids, label_ids

def create_model(session, 
                 source_vocab_size, 
                 target_vocab_size, 
                 label_vocab_size):
  """Create model and initialize or load parameters in session."""

  with tf.variable_scope("model", reuse=None):#True
    model_test = multi_task_model.MultiTaskModel(
          source_vocab_size, 
          # target_vocab_size,
          # label_vocab_size,
          target_vocab_size,
          source_vocab_size,
          _buckets,
          FLAGS.word_embedding_size, 
          FLAGS.size, 
          FLAGS.num_layers, 
          FLAGS.max_gradient_norm, 
          FLAGS.batch_size,
          dropout_keep_prob=FLAGS.dropout_keep_prob, 
          use_lstm=True,
          forward_only=True, 
          use_attention=FLAGS.use_attention,
          bidirectional_rnn=FLAGS.bidirectional_rnn,
          task=task)


  ckpt = tf.train.get_checkpoint_state(FLAGS.model_dir)
  if ckpt:
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model_test.saver.restore(session, ckpt.model_checkpoint_path)

  else:
    print("Created model with fresh parameters.")
    session.run(tf.global_variables_initializer())

  return  model_test #model_train,


date_set = data_utils.prepare_multi_task_data(
FLAGS.data_dir, FLAGS.in_vocab_size, FLAGS.out_vocab_size)
date_set = list(date_set)
vocab_path = ''
tag_vocab_path = ''
label_vocab_path = ''
in_seq_train, out_seq_train, label_train = date_set[0]
in_seq_dev, out_seq_dev, label_dev = date_set[1]
# print('dateset: ', date_set)
in_seq_test, out_seq_test, label_test = date_set[2]
vocab_path, tag_vocab_path, label_vocab_path = date_set[3]
result_dir = FLAGS.model_dir + '/test_results'
if not os.path.isdir(result_dir):
    os.makedirs(result_dir)

current_taging_valid_out_file = result_dir + '/tagging.valid.hyp.txt'
current_taging_test_out_file = result_dir + '/tagging.test.hyp.txt'
vocab, rev_vocab = data_utils.initialize_vocab(vocab_path)
tag_vocab, rev_tag_vocab = data_utils.initialize_vocab(tag_vocab_path)
label_vocab, rev_label_vocab = data_utils.initialize_vocab(label_vocab_path)
test_set = read_data_test(in_seq_test, out_seq_test, label_test)
dev_set = read_data(in_seq_dev, out_seq_dev, label_dev)
# print('dev set: ', dev_set)
train_set = read_data(in_seq_train, out_seq_train, label_train)
train_bucket_sizes = [len(train_set[b]) for b in xrange(len(_buckets))]
train_total_size = float(sum(train_bucket_sizes))

train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                       for i in xrange(len(train_bucket_sizes))]

# def load_model():
#   print ('Applying Parameters:')
#
#   config = tf.ConfigProto(
#       gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.23),
#       #device_count = {'gpu': 2}
#   )
#
#   sess = tf.Session(config=config)
#   model_test = create_model(sess,
#                      len(vocab),
#                      len(tag_vocab),
#                      len(label_vocab))
#   if sess:
#       print('12345')
#   if model_test:
#       print(23456)
#   return sess, model_test

# #
# sess, model_test = load_model()

def run_valid_test(data_set, mode, model_test, sess): # mode: Eval, Test
    # Run evals on development/test set and print the accuracy.
    word_list = list()
    ref_tag_list = list()
    hyp_tag_list = list()
    ref_label_list = list()
    hyp_label_list = list()
    correct_count = 0
    accuracy = 0.0
    tagging_eval_result = dict()
    for bucket_id in xrange(len(_buckets)):
      eval_loss = 0.0
      count = 0
      for i in xrange(len(data_set[bucket_id])):
        count += 1
        # print(len(data_set))
        sample = model_test.get_one_test(data_set, bucket_id, i)
        encoder_inputs,tags,tag_weights,sequence_length,labels = sample
        # print(tags)
        # print(sequence_length)
        tagging_logits = []
        class_logits = []
        if task['tagging'] == 1:
          step_outputs = model_test.tagging_step(sess,
                                                 encoder_inputs,
                                                 tags,
                                                 tag_weights,
                                                 sequence_length,
                                                 bucket_id,
                                                 True)
          _, step_loss, tagging_logits = step_outputs


        eval_loss += step_loss / len(data_set[bucket_id])
        hyp_label = None
        if task['tagging'] == 1:
            if mode == 'Eval':
                ref_tag_list.append([rev_tag_vocab[x[0]] for x in \
                                     tags[:sequence_length[0]]])
            word_list.append([rev_vocab[x[0]] for x in \
                            encoder_inputs[:sequence_length[0]]])
            hyp_tag_list.append(
                  [rev_tag_vocab[np.argmax(x)] for x in \
                                 tagging_logits[:sequence_length[0]]])
    accuracy = float(correct_count)*100/count
    if task['tagging'] == 1:
      if mode == 'Test':
          taging_out_file = current_taging_test_out_file
          print(len(word_list))
          print(len(hyp_tag_list))
          print(word_list)
          tagging_eval_result = conlleval_test(hyp_tag_list,
                                          word_list,
                                          taging_out_file)
          return tagging_eval_result
      sys.stdout.flush()


class Model(object):
    def __init__(self):
        self.config = config = tf.ConfigProto(gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.23),
      #device_count = {'gpu': 2}
    )
        self.sess = tf.Session(config=self.config)
        self.model_test = create_model(self.sess,
                     len(vocab),
                     len(tag_vocab),
                     len(label_vocab))

        self.mode = 'Test'
    def predict(self, test_set):
        print('debuggs')
        print(test_set)
        test_tagging_result = run_valid_test(test_set, self.mode, self.model_test, self.sess)



def main(_):
    model = Model()
    model.predict(test_set)




if __name__ == "__main__":
  tf.app.run()
