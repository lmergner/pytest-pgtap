#!/usr/local/env bash
set -ex

CWD=$(pwd)

version="v0.99.0"
working=$TMPDIR/pgtap-${version}

if [ -d ${working} ]; then
    rm -rf ${working}
fi

git clone git://github.com/theory/pgtap.git ${working}
cd ${working}
git checkout tags/${version}
make
make installcheck
make install
cd $PWD
rm -rf $TMPDIR/pgtap