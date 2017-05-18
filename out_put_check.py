from os import walk
import os
import csv
import click

suffixes_rdf = ['_linkingdata.rdf', '_linkingdata_sections.rdf', '_bio2rdf_sections.rdf', '_bio2rdf.rdf']
suffixes_annotations = ['_bio2rdf_ncbo_annotations_OA.rdf', '_linkingdata_ncbo_annotations_OA.rdf']


def check_output(input_dir, output_dir, suffixes, log_file, move):
    input_list = get_file_names(input_dir)
    input_list = [input_file.replace('.nxml', '') for input_file in input_list if 'PMC' in input_file]

    output_list = get_file_names(output_dir)
    logs = []

    for input_pmc in input_list:
        pmc_log = create_log_dict(input_pmc, suffixes)
        for suffix in suffixes:
            output_name = input_pmc + suffix
            output_file_path = output_dir + output_name
            if output_name not in output_list:
                pmc_log[suffix] = 'FILE_NOT_EXIST'
                if move:
                    move_input(input_dir, input_pmc + '.nxml')
            elif os.stat(output_file_path).st_size == 0:
                pmc_log[suffix] = 'EMPTY_FILE'
                if move:
                    move_input(input_dir, input_pmc + '.nxml')
        logs.append(pmc_log)
    with open(log_file, 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, logs[0].keys())
        w.writeheader()
        for row in logs:
            w.writerow(row)


def create_log_dict(pmc, suffixes):
    log = dict(pmc=pmc)
    for suffix in suffixes:
        log[suffix] = 'GENERATED'
    return log


def get_file_names(directory):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(directory):
        file_list.extend(filenames)
        break
    return file_list


def move_input(input_dir, input_file):
    if not os.path.exists(input_dir + 'unprocessed'):
        os.makedirs(input_dir + 'unprocessed')
    if not os.path.isfile(input_dir + 'unprocessed/' + input_file):
        os.rename(input_dir + input_file, input_dir + 'unprocessed/' + input_file)


@click.command()
@click.option('--input_dir', default='./', help='Path to the corpus directory. Default = ./')
@click.option('--output_dir', default='./', help='Path to the output directory. Default = ./')
@click.option('--metadata', is_flag=True)
@click.option('--annotation', is_flag=True)
@click.option('--move', is_flag=True)
def cli(input_dir, output_dir, metadata, annotation, move):
    if metadata:
        check_output(input_dir, output_dir, suffixes_rdf, 'log_metadata.csv', move)
        return
    if annotation:
        check_output(input_dir, output_dir, suffixes_annotations, 'log_annotation.csv', move)
        return


if __name__ == '__main__':
    cli()
