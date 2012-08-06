PROJECT="wanalytics"

# check if then the operation is required
CUSTOM_HOME=$HOME
VIRTUALENV_BIN=virtualenv
if [ -n "${OPENSHIFT_RUNTIME_DIR}" ]; then
    echo "Openshift environment detected"
    CUSTOM_HOME=$OPENSHIFT_DATA_DIR
    VIRTUALENV_BIN=$OPENSHIFT_RUNTIME_DIR/bin/virtualenv
fi
echo "using home " ${CUSTOM_HOME}
mkdir -p ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}
touch ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/requirements.txt

mkdir -p "src/main/webapp/WEB-INF/lib-python/"
echo "${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/lib/python2.7/site-packages" > "src/main/webapp/WEB-INF/lib-python/site-packages-path.txt"

if diff requirements.txt ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/requirements.txt >/dev/null ; then
    $VIRTUALENV_BIN ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}
    . ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/bin/activate
    pip install -r requirements.txt
    echo "requirements file did not change since the last run. exiting...."
else
    rm -r ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/
    mkdir -p ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/
    # pip cache
    #
    mkdir -p ${CUSTOM_HOME}/.pip_download_cache
    export PIP_DOWNLOAD_CACHE=${CUSTOM_HOME}/.pip_download_cache
    #
    #
    $VIRTUALENV_BIN ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}
    . ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/bin/activate
    pip install -r requirements.txt
    #
    cp requirements.txt ${CUSTOM_HOME}/pyvirtualenv/${PROJECT}/
    deactivate
fi
