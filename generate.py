from os import walk
import os
import subprocess
from shutil import copyfile, rmtree, copytree
import click
import time


def generate(input_dir, output_dir, biotea_command):
    if biotea_command == 'metadata':
        biotea_command = ['java', '-jar', 'biotea_rdfization.jar', '-in', input_dir + 'in_process', '-out', output_dir]
    else:
        biotea_command = ['java', '-jar', 'biotea_annotation.jar', '-in', input_dir + 'in_process', '-out', output_dir,
                          '-extension', 'nxml', '-inStyle', 'jats_file', '-onto', 'OA', '-annotator', 'ncbo']
    input_list = get_file_names(input_dir)
    if not os.path.exists(input_dir + 'in_process'):
        copytree('aux/', input_dir + 'in_process')
    cont = 0
    for file_name in input_list:
        copyfile(input_dir + file_name, input_dir + 'in_process/' + file_name)
        cont += 1
        if cont == 1000:
            cont = 0
            call_biotea(biotea_command)
            rmtree(input_dir + 'in_process/')
            copytree('aux/', input_dir + 'in_process')
    call_biotea(biotea_command)
    rmtree(input_dir + 'in_process/')


def get_file_names(directory):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(directory):
        file_list.extend(filenames)
        break
    return file_list


def call_biotea(biotea_command):
    retries = 0
    retry = True
    while retry and retries < 3:
        biotea_out = subprocess.check_output(biotea_command)
        if biotea_out.find('ERROR NCBO Annotator') != -1 and biotea_out.find('(http call)') != -1:
            click.secho('NCBO Annotator HTTP Error, wait for retry: ' + str(retries), fg='red', bold=True)
            time.sleep(5)
            retry = True
            retries += 1
        else:
            retry = False


@click.command()
@click.option('--input_dir', default='./', help='Path to the corpus directory. Default = ./')
@click.option('--output_dir', default='./', help='Path to the output directory. Default = ./')
@click.option('--metadata', is_flag=True)
@click.option('--annotation', is_flag=True)
def cli(input_dir, output_dir, metadata, annotation):
    if metadata:
        generate(input_dir, output_dir, 'metadata')
        return
    if annotation:
        generate(input_dir, output_dir, 'annotation')
        return


if __name__ == '__main__':
    cli()