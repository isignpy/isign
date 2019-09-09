platform="$(uname -s)"
if [[ "$platform" == 'Darwin' ]]; then
    export PATH="/usr/local/opt/openssl@1.1/bin:$PATH"
    export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib -L/usr/local/opt/libffi/lib $LDFLAGS"
    export CFLAGS="-I/usr/local/opt/openssl@1.1/include $CFLAGS"
    export CPPFLAGS=$CFLAGS
fi
