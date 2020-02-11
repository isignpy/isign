# Signer modules

## Rationale

At its core, `isign` is simply doing cryptographic signatures
of certain parts of your app, and then inserting those signatures into a new copy of your app.
 
Sometimes, you might need a more custom way of performing these cryptographic signatures. 
Perhaps you would prefer not to use `openssl` or use PEM files. Maybe, for security reasons, you can't store
your private keys locally and you need to use a hardware security module.

You can simply write a Python module to interface with your preferred way to sign data, and invoke it on the 
command line.

## Typical usage

```bash
# Simplest possible invocation
$ isign --signer=MySigner -o resigned.ipa original.ipa
archived Ipa to /home/alice/resigned.ipa

# Pass some arguments to initialize your signer
$ isign --signer=AnotherSigner --signerArg='foo=bar' --signerArg='quux=quuux' \
        -o resigned.ipa original.ipa
archived Ipa to /home/alice/resigned.ipa        
```

```python
isign.resign(
   'original.ipa',
   output_file='resigned.ipa'
   signer_class=AnotherSigner,   # your class name, must be in $PYTHONPATH 
   signer_arguments={            # arguments to initialize the signer
      'foo': 'bar'
      'quux': 'quux'
   }
)
```

## How to write a Signer module

### Where to put it

The module will be invoked by name, much as if it were the result of an `import MySigner` python commans. 
You will need to create an appropriate Python module that is 
available within your `$PYTHONPATH`. See Python documentation for more instructions about that.

### How to write it

There are a few sample signer modules included in the tests folder, that may be helpful when writing your own.

* [SimpleSigner](tests/testPythonLibDir/SimpleSigner) does nothing, and just prints to STDOUT when signing is invoked.
* [CallbackSigner](tests/testPythonLibDir/CallbackSigner) also does nothing, but calls a callback when signing is invoked.
* [RemotePkcs1Signer](tests/testPythonLibDir/CallbackSigner) is part of our end-to-end test, and makes calls to an [HTTP service](tests/signing_service.py) to do real [PKCS#1](https://en.wikipedia.org/wiki/PKCS_1) signing.

#### Initialization

Your Signer class can be initialized with whatever arguments you like.

As in the examples above, you can pass those initialization arguments on the command line or via a Python program.


#### Interface

Your class, once initialized as on object, must implement one method:

##### `sign(self, data)`

`data` is a string, potentially very large.

This method must return a string, a signature of the given data.

The signature is a [CMS](https://en.wikipedia.org/wiki/Cryptographic_Message_Syntax) signature of the 
given data in [DER](https://wiki.openssl.org/index.php/DER) form.

The signing key must be the private key of the public-private pair registered to your Apple developer 
organization. Depending on how you're doing this, it may have already been provided to your class in the 
`signer_key_file`. The signing certificate must be the Apple-provided certificate for your developer organization. 
This may have been already provided in the `signer_cert_file`. See the [documentation on credentials](credentials.md) 
for details on keys and certificates.

You must also incorporate the [current public Apple certificate(s)](applecerts.md) as an additional certificate. This 
should be provided to your class as `apple_cert_file`.

Also see the implementation of isign's `Signer.sign` for hints. This is not a trivial thing to get right, so take your
time and be patient.


## Hints on secure design

### General principles
There is only one element of signing that absolutely must remain private: the private key.

Everything else is public knowledge. Your certificate, and Apple's certificates, can be passed around in the clear.

Consequently, if you need to store your keys in an HSM, you can make life easier on yourself by treating some or
all of the certificates as information you pass in as arguments. Your certificate just needs to be paired with 
the right key.

### Invocation
Be aware that command line arguments aren't secure. Other users can see the exact command you are running, and 
it might be stored in your shell's `history`. So avoid doing things like `--signerArg='password=hunter2'`.

For passing sensitive configuration into your signer module, you should consider other strategies.

* Pass the path to a configuration file, like, `--signerArg='config=~/alice/signerconfig.json` 
  with appropriately secure permissions on that file
* Use environment variables. They will be available to your entire process, including within your signer class.
