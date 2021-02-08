# Author: 14281055 Liheng Chen CIT BJTU
# File Name:

import numpy
import os
import xlrd
import xlsxwriter


def excel_to_np_array(path):
    r_workbook = xlrd.open_workbook(path)
    r_sheet = r_workbook.sheet_by_index(0)
    matrix = []
    for rowx in range(r_sheet.nrows):
        row_array = []
        for colx in range(r_sheet.ncols):
            row_array.append(r_sheet.cell_value(rowx, colx))
        matrix.append(row_array)
    return numpy.array(matrix)


def np_array_to_excel(np_array, path):
    w_workbook = xlsxwriter.Workbook(path)
    w_sheet = w_workbook.add_worksheet()
    for rowx in range(np_array.shape[0]):
        for colx in range(np_array.shape[1]):
            w_sheet.write(rowx, colx, np_array[rowx][colx])
    w_workbook.close()


class BPNeuralNetwork(object):
    def sigmoid(self, x, derivation=False):
        if derivation:
            return self.sigmoid(x) * (1 - self.sigmoid(x))
        else:
            return 1 / (1 + numpy.exp(-x))

    input_data = None
    output_data = None

    layer_input_list = None
    layer_output_list = None

    layer_bias = None

    layer_number = None
    layer_node_number_list = None

    weight_list = []
    correction_matrix_list = []

    layer_output_delta_list = None
    layer_error_list = None

    activation_func = sigmoid

    epochs = 100000000
    goal = 0.00001
    learn_rate = 0.1  # usually in (0,0.1); annealing
    correct_rate = 0.1  # annealing

    loss = None

    weight_file_path = None

    def __init__(self, layer_node_number_list, input_data=None, output_data=None, weight_file_path=None):
        self.layer_node_number_list = layer_node_number_list

        self.input_data = input_data
        self.output_data = output_data

        self.weight_file_path = weight_file_path

        self.layer_number = len(self.layer_node_number_list)

        self.layer_bias = [0] * (self.layer_number - 1)

        self.layer_input_list = [numpy.array(None)] * self.layer_number
        self.layer_output_list = [numpy.array(None)] * self.layer_number

        self.layer_output_delta_list = [numpy.array(None)] * self.layer_number
        self.layer_error_list = [numpy.array(None)] * self.layer_number

        for layer_index in range(self.layer_number - 1):
            self.weight_list.append(numpy.random.randn(
                layer_node_number_list[layer_index],
                layer_node_number_list[layer_index + 1]
            ) / numpy.sqrt(self.layer_node_number_list[layer_index]))
            self.correction_matrix_list.append(numpy.zeros(self.weight_list[layer_index].shape))
        if self.weight_file_path is not None and os.path.exists(self.weight_file_path):
            self.weight_list = numpy.load(self.weight_file_path)

    def train(self):
        for epoch in range(self.epochs):
            self.forward_propagation(self.input_data)
            self.loss = numpy.square(self.output_data - self.layer_output_list[-1]).sum() / 2
            if self.loss < self.goal:
                break
            self.back_propagation(self.output_data)
            self.annealing(epoch)
            print('\rEpoch:%d Loss:%f' % (epoch, self.loss), end='')
        self.save_weight()

    def test(self):
        self.forward_propagation(self.input_data)
        return self.layer_output_list[-1]

    def forward_propagation(self, input_data):
        self.layer_input_list[0] = input_data
        self.layer_output_list[0] = input_data
        for layer_index in range(1, self.layer_number):
            self.layer_input_list[layer_index] = \
                self.layer_output_list[layer_index - 1].dot(self.weight_list[layer_index - 1]) + \
                self.layer_bias[layer_index - 1]
            self.layer_output_list[layer_index] = self.activation_func(self.layer_input_list[layer_index])

    def back_propagation(self, output_data):
        self.layer_output_delta_list[-1] = output_data - self.layer_output_list[-1]
        self.layer_error_list[-1] = \
            self.layer_output_delta_list[-1] * \
            self.activation_func(
                self.layer_input_list[-1],
                derivation=True
            )
        self.weight_list[-1] += self.learn_rate * self.layer_output_list[-2].T.dot(
            self.layer_error_list[-1]) + self.correct_rate * self.correction_matrix_list[-1]
        self.correction_matrix_list[-1] = self.layer_output_list[-2].T.dot(self.layer_error_list[-1])
        for layer_index in range(-2, -self.layer_number, -1):
            self.layer_output_delta_list[layer_index] = \
                self.layer_error_list[layer_index + 1].dot(self.weight_list[layer_index + 1].T)
            self.layer_error_list[layer_index] = \
                self.layer_output_delta_list[layer_index] * \
                self.activation_func(
                    self.layer_input_list[layer_index],
                    derivation=True
                )
            self.weight_list[layer_index] += \
                self.learn_rate * self.layer_output_list[layer_index - 1].T \
                    .dot(self.layer_error_list[layer_index]) \
                + self.correct_rate * self.correction_matrix_list[layer_index]
            self.correction_matrix_list[layer_index] = self.layer_output_list[layer_index - 1].T \
                .dot(self.layer_error_list[layer_index])

    def annealing(self, epoch, step=100000):
        if epoch % step == 0:
            self.learn_rate /= 2  # learn rate annealing
            self.correct_rate /= 2

    def save_weight(self):
        if self.weight_file_path is not None:
            if os.path.exists(self.weight_file_path):
                os.remove(self.weight_file_path)
            numpy.save(os.path.splitext(self.weight_file_path)[0], self.weight_list)


def train(layer_node_number_list, train_input_file_path, train_output_file_path, weight_file_path=None):
    train_input_data = excel_to_np_array(train_input_file_path)
    train_output_data = excel_to_np_array(train_output_file_path)

    bp_neural_network = BPNeuralNetwork(layer_node_number_list, weight_file_path=weight_file_path)
    for index in range(train_input_data.shape[0]):
        print('Round:%d' % index)
        bp_neural_network.input_data = numpy.atleast_2d(train_input_data[index])
        bp_neural_network.output_data = numpy.atleast_2d(train_output_data[index])
        bp_neural_network.train()
        print()
    bp_neural_network.input_data = train_input_data
    bp_neural_network.output_data = train_output_data
    bp_neural_network.train()


def test(layer_node_number_list, test_input_file_path, predict_output_file_path, weight_file_path):
    bp_neural_network = BPNeuralNetwork(
        layer_node_number_list,
        excel_to_np_array(test_input_file_path),
        weight_file_path=weight_file_path
    )
    np_array_to_excel(bp_neural_network.test(), predict_output_file_path)


if __name__ == '__main__':
    train(
        [10, 12, 12, 12, 12, 1],
        r'C:\Users\陈力恒\Downloads\BPNN\train_input.xlsx',
        r'C:\Users\陈力恒\Downloads\BPNN\train_output.xlsx',
        r'C:\Users\陈力恒\Downloads\BPNN\weight.npy'
    )
    test(
        [10, 12, 12, 12, 12, 1],
        r'C:\Users\陈力恒\Downloads\BPNN\test_input.xlsx',
        r'C:\Users\陈力恒\Downloads\BPNN\predict_output.xlsx',
        r'C:\Users\陈力恒\Downloads\BPNN\weight.npy'
    )
