#!/usr/bin/env python

#Author: Aretas Gaspariunas
# the controller of the script; including CLI arguments; file format check etc.
# both files must be in the same folder to be executable (controller.py and find_ORF.py)

if __name__ == '__main__':

    import argparse
    from find_ORF import *

    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-i', '--fasta',
        help='Specify the FASTA file with a DNA nucleotide sequence for the ORF detection', required=True)
    optional.add_argument('-l', '--min_ORF_len',
        help='Specify the minimum nucleotide length for the ORF detection; default = 300 NT', default=300, type=int)
    optional.add_argument('-p', '--translate',
        help='Include the flag if you wish to translate ORFs to peptide sequences', action='store_true')
    optional.add_argument('-t', '--table',
        help='Specify the translation table. Please see BioPython documentation', default=1, type=int)
    optional.add_argument('-o', '--stdout',
        help='Specify the flag for an output in a text file in FASTA format', action='store_true')
    optional.add_argument('-n', '--ignore_ambiguous',
        help="Specify if ORFs with ambiguous calls (containing 'N') to be included in the output", action='store_true')
    optional.add_argument('-c', '--start_codon',
        help='Specify if you want to use a different start codon', default='ATG', type=str)
    args = parser.parse_args()

    def writting_file (dictionary, output):
        for key, value in dictionary.items():
            if args.translate is True:
                prot_seq = str(Seq(value.sequence).translate(args.table))
                # prot_seq = str((value.sequence).translate(args.table))
                sequence = '\n'.join(prot_seq[f:f+60] for f in range(0, len(prot_seq), 60))
                output_str = '{0}|STRAND_{1}_FRAME_{2}_LENGTH_{3}_START_{4}\n{5}\n'\
                    .format(value.tag.upper(), value.strand, value.frame, len(prot_seq), value.start, sequence)
                output.write(output_str)
            else:
                sequence = '\n'.join(value.sequence[f:f+60] for f in range(0, len(value.sequence), 60))
                output_str = '{0}|STRAND_{1}_FRAME_{2}_LENGTH_{3}_START_{4}\n{5}\n'\
                    .format(value.tag.upper(), value.strand, value.frame, len(value.sequence), value.start, sequence)
                output.write(output_str)
        return output

    try:
        with open(args.fasta, 'r') as f:
            first_line = f.readline().strip('\n')
            if first_line.startswith('>'):
                print ('The input file format seems to match FASTA! Proceeding...')
                second_line = f.readline().strip('\n').upper()
                if re.search(r'U', second_line):
                    print ('The sequence appears to be a RNA sequence. Please use a DNA sequence!')
                    exit()
                elif re.match(r'A|T|C|G', second_line):
                    sequence = ''.join([second_line, f.read().replace('\n', '')])
                    new_object = DNAsequence(sequence, first_line)
                    orf_forward_dict = new_object.find_ORF(new_object.sequence, args.min_ORF_len, '+1', args.start_codon, args.ignore_ambiguous)
                    orf_rev_dict = new_object.find_ORF(new_object.rev_compliment(), args.min_ORF_len, '-1', args.start_codon, args.ignore_ambiguous)

                    if args.stdout:
                        with open(args.fasta.split(".")[0] + '_{0}_ORF.fasta'.format(args.min_ORF_len), 'w') as out_file:
                            writting_file (orf_forward_dict, out_file)
                            writting_file (orf_rev_dict, out_file)

                    print ('{0} ORF(s) have been detected across all 6 reading frames.'.format(len(orf_forward_dict) + len(orf_rev_dict)))
                else:
                    print ('The FASTA file does not contain a nucleotide sequence!')
            else:
                print ('Wrong file format! The input file must be in FASTA format')
                exit()
    except IOError:
        print ('Could not open the file!', args.fasta)
