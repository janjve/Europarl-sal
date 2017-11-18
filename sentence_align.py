from os.path import join
from enum import Enum


class SalMethod(Enum):
    intersect = 'intersection'
    union = 'union'

    def __str__(self):
        return self.value


class SentenceAligner:
    def __init__(self, languages, input_path, output_path, connecting_language):
        if connecting_language in languages:
            languages.remove(connecting_language)

        input_path_pattern = join(input_path, 'europarl-v7.{0}-{1}.{0}')
        input_path_cl_pattern = join(input_path, 'europarl-v7.{0}-{1}.{1}')  # connecting_language.
        output_path_pattern = join(output_path, 'mono.{0}.txt')

        self.input_iterators = [open(input_path_pattern.format(lang, connecting_language), 'r', encoding='utf-8')
                                for lang in languages]
        self.input_iterators_cl = [open(input_path_cl_pattern.format(lang, connecting_language), 'r', encoding='utf-8')
                                   for lang in languages]

        self.output_iterators = [open(output_path_pattern.format(lang), 'w', encoding='utf-8') for lang in languages]
        self.output_iterator_cl = open(output_path_pattern.format(connecting_language), 'w', encoding='utf-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Flushing ...")
        [f.close() for f in self.input_iterators]
        [f.close() for f in self.input_iterators_cl]
        [f.close() for f in self.output_iterators]
        self.output_iterator_cl.close()

    @staticmethod
    def read_sentences(ite1, ite2):
        sal_sentences = {}
        for row_cl, row in zip(ite1, ite2):
            row_cl = row_cl.strip()
            row = row.strip()
            if row_cl and row_cl not in sal_sentences:  # Only take unique sentences. We favor first appearance.
                sal_sentences[row_cl] = row
        return sal_sentences

    def write_line(self, cl_sentence, sentences):
        self.output_iterator_cl.write(cl_sentence + "\n")
        for iterator, sentence in zip(self.output_iterators, sentences):
            iterator.write(sentence + "\n")

    def run_alignment(self, sal_method):
        cl2l = [{}] * len(self.input_iterators_cl)  # list of connecting language -> language

        # Read pair-wise-sal
        print('Reading from files ...')
        for lang_index in range(len(self.input_iterators_cl)):
            cl2l[lang_index] = self.read_sentences(self.input_iterators_cl[lang_index], self.input_iterators[lang_index])

        cl_sentence_set_list = map(lambda x: set(x.keys()), cl2l)

        print('Printing to files ...')
        # Union method. Padding with empty lines.
        if sal_method == SalMethod.union:
            for cl_sentence in set.union(*cl_sentence_set_list):
                output_sentences = map(lambda cl2lang: cl2lang[cl_sentence] if cl_sentence in cl2lang else "", cl2l)
                self.write_line(cl_sentence, output_sentences)

        # Intersection method. No padding required.
        elif sal_method == SalMethod.intersect:
            for cl_sentence in set.intersection(*cl_sentence_set_list):
                output_sentences = map(lambda cl2lang: cl2lang[cl_sentence], cl2l)
                self.write_line(cl_sentence, output_sentences)

        # Should never happen
        else:
            print('Unexpected sal_method.')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--languages', help='<Required> input languages', nargs='+', required=True)
    parser.add_argument('-i', '--input_path', help='<Required> input path', required=True)
    parser.add_argument('-o', '--output_path', help='output path')
    parser.add_argument('-cl', '--connecting_language', help='connecting language', default='en')
    parser.add_argument('-m', '--sal_method', help='Sentence align method.', type=SalMethod,
                        choices=list(SalMethod), default=SalMethod.union)
    args = parser.parse_args()

    # Use input as output if no output is specified.
    if not args.output_path:
        args.output_path = args.input_path

    print("Languages:\t", args.languages)
    print("Connecting:\t", args.connecting_language)
    print("Input_path:\t", args.input_path)
    print("Output_path:\t", args.output_path)

    with SentenceAligner(args.languages, args.input_path, args.output_path, args.connecting_language) as wa:
        wa.run_alignment(args.sal_method)
