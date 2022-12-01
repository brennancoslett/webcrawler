# Fix openssl 3.0 crash on ubuntu 22.04
export OPENSSL_CONF=openssl.cnf
python3 crawler ${@}