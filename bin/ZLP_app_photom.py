#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 
Zero Level Pipeline apperture photometry 

Usage: 
  ZLP_app_photom [options] (-c <CONFMAP> | --confmap <CONFMAP>) (-C <CATFILE> | --catfile <CATFILE>) (-f <FILELIST> | --filelist <FILELIST> | INPUT ...)

Options:
  -h --help              Show help text
  --verbose              Print more text
  --dist=DISTMAP         The path to the relevent distortion 
  --outlist=OUTLIST      Specify the name of the list of completed files
  --nproc=NPROC          Enable multithreading if you're analysing a lot of files at once [default: 1]
  --apsize=APSIZE        The radius of the apperture you wish to use in the photometry stage [default: 2]
  --s_thresh=S_THRESH    The detection threshold to use when WCS solving images - typically higher than when doing actual photometry [default: 7]
  --catsrc=CATSRC        What catalogue to use during catalog matching [default: viz2mass]
  --catpath=CATPATH      If you're using a local catalog for cat matching, where is it? [default: False]
  --outdir=OUTDIR        Where you would like the result files to go [default: ./]

This is the apperture photometry portion of the pipeline. It can be driven either in a list mode
or on a single file
 
"""
import sys
import linecache
from numpy import *
import threading
from os.path import isfile, join
from NGTS_workpackage import *
import json
import argparse


def main(argv):
    #if you don't provide an outlist name i'll assume you just want to add _phot to the end
    if not argv.outlist:
        argv.outlist = argv.filelist + '_phot'

    outfile = open(argv.outlist, 'w')
    outfile.close()

    dist_map = extract_dist_map(argv.dist)

    if not argv.norunwcs:
        m_solve_images(argv.filelist, argv.outlist, dist_map, argv.wcsref,
                       nproc=argv.nproc,
                       thresh=argv.s_thresh,
                       verbose=argv.verbose,
                       catsrc=argv.catsrc)
    m_wcs_photom(argv.filelist, argv.outlist, argv.apsize, argv.confmap, argv.catfile,
                 nproc=argv.nproc,
                 verbose=argv.verbose)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--confmap", help="Confidence map", required=True)
    parser.add_argument("-C", '--catfile', help='Input catalogue', required=True)
    parser.add_argument('-f', '--filelist', help='List of files', required=True)
    parser.add_argument('--dist', help='Path to the relevant distortion', required=True)
    parser.add_argument('--outdir', required=True, help='Output directory')
    parser.add_argument('--wcsref', help='WCS reference frame')

    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--outlist', help="List of completed files")
    parser.add_argument('--nproc', type=int, default=1, help='Number of processors')
    parser.add_argument('--apsize', type=float, default=2, help='Aperture size')
    parser.add_argument('--s_thresh',
                        type=float,
                        default=7,
                        help='Detection threshold in sigma')
    parser.add_argument('--catsrc',
                        default='localfits',
                        help='Catalogue for wcs solving')
    parser.add_argument('--catpath',
                        default='catcache',
                        help='Local casutools catalogue cache')
    parser.add_argument('--norunwcs',
                        action='store_true',
                        default=False,
                        help='Do not astrometrically solve the images')

    main(parser.parse_args())
