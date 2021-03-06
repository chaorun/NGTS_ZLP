abspath() {
    python -c "import os; print os.path.realpath('${1}')"
}

BASEDIR=$(abspath $(dirname $0))
PIPELINEDIR="${BASEDIR}/../zlp-script"
STDERRFILE=/tmp/test.stderr
STDOUTFILE=/tmp/test.stdout


setup_environment() {
    export PYTHONPATH=${BASEDIR}:${BASEDIR}/testdata:${PIPELINEDIR}/scripts:${PYTHONPATH}
    OUTFILE=$(find ${BASEDIR}/testdata -name 'output.fits')
    if [ ! -z ${OUTFILE} ]; then
        if [ -f ${OUTFILE} ]; then
            rm ${OUTFILE}
        fi
    fi
}

run_test() {
    local readonly filelist_name=$(create_filelist)
    python ./bin/ZLP_create_outfile.py \
        --outdir ${BASEDIR}/testdata \
        ${filelist_name} \
        --apsize 2 \
        --nproc 1
}

assert_output() {
    assert_npts_correct
    assert_tmid_sorted
}

assert_tmid_sorted() {
python - <<EOF
import fitsio
import numpy as np
with fitsio.FITS("testdata/output.fits") as infile:
    imagelist = infile['imagelist'].read()
tmid = imagelist['TMID']
assert (tmid == np.sort(tmid)).all(), tmid
EOF
}

assert_npts_correct() {
python - <<EOF
import fitsio
with fitsio.FITS("testdata/output.fits") as infile:
    catalogue = infile['catalogue']
    keys = catalogue.get_colnames()
    value_ind = keys.index('NPTS')
    nrows = catalogue.get_nrows()
    flux = infile['flux'].read()
    assert flux.shape[0] == nrows

    for (lc, cat_row) in zip(flux, catalogue):
        value = cat_row[value_ind]
        target = lc[lc == lc].size
        assert value == target, (value, target)
EOF
}

check_for_failure() {
    if [[ "$?" == "0" ]]; then
        echo "Pass"
    else
        echo "Fail"
        cat ${STDERRFILE}
        exit 1
    fi
}

main() {
    (cd ${BASEDIR}
    setup_environment

    echo -n "Running test... "
    set +e
    run_test 2>${STDERRFILE} >${STDOUTFILE}
    check_for_failure
    set -e
    echo -n "Running test... "
    assert_output
    check_for_failure
    )
}
