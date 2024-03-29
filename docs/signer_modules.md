# Signer modules

## Rationale

At its core, `isign` is simply doing cryptographic signatures
of certain parts of your app, and then inserting those signatures into a new copy of your app.
 
Sometimes, you might need a more custom way of performing these cryptographic signatures. Maybe, for security reasons, you can't store your private keys locally in PEM files. Maybe you want to use some sort of system which manages your secrets, or even does the signing for you somewhere else.

You can simply write a Python module to interface with your preferred way to sign data, and invoke it on the 
command line.

## Typical usage

### Command line
```bash
# Simplest possible invocation
$ isign --signer=MySigner -o resigned.ipa original.ipa
archived Ipa to /home/alice/resigned.ipa

# Pass some arguments to initialize your signer
$ isign --signer=AnotherSigner --signerArg='foo=bar' --signerArg='quux=quuux' \
        -o resigned.ipa original.ipa
archived Ipa to /home/alice/resigned.ipa        
```

### Python
```python
isign.resign(
   'original.ipa',
   output_file='resigned.ipa'
   signer_class=AnotherSigner,   # your class name, must be in $PYTHONPATH 
   signer_arguments={            # arguments to initialize the signer
      'foo': 'bar'
      'quux': 'quuux'
   }
)
```

## How to write a Signer module

### Where to put it

The module will be invoked by name, much as if it were the result of an `import MySigner` Python command. 
You will need to create an appropriate Python module that is 
available within your `$PYTHONPATH`. See Python documentation for more instructions about that.

### How to write it

There are a few sample signer modules included in the tests folder, that may be helpful when writing your own.

* [SimpleSigner](../tests/TestPythonLibDir/SimpleSigner/__init__.py) does nothing, and just prints to STDOUT when signing is invoked.
* [CallbackSigner](../tests/TestPythonLibDir/CallbackSigner/__init__.py) also does nothing, but calls a callback when signing is invoked.
* [RemotePkcs1Signer](../tests/TestPythonLibDir/RemotePkcs1Signer/__init__.py) is part of our end-to-end test, and makes calls to an [HTTP service](../tests/signing_service.py) to do real [PKCS#1](https://en.wikipedia.org/wiki/PKCS_1) signing.

#### Initialization

Your Signer class can be initialized with whatever arguments you like.

As in the examples above, you can pass those initialization arguments on the command line or via a Python program.

#### Interface

Your class, once initialized as on object, must implement one method:

##### `sign(self, data)`

`data` is a string, potentially very large.

The method should return a [PKCS#1 signature](https://en.wikipedia.org/wiki/PKCS_1), as a Python string, in DER form. 

For a sample of exactly what signature you should produce with standard Python crypto modules, see the implementation of [Signer.PKCS1Signer](../isign/signer.py). It's very simple!


## Hints on secure design

### General principles
There is only one element of signing that absolutely must remain private: the private key.

Everything else is public knowledge. Your certificate, and Apple's certificates, can be passed around in the clear.

### Invocation
Be aware that command line arguments aren't secure. Other users can see the exact command you are running, and 
it might be stored in your shell's `history`. So avoid doing things like `--signerArg='password=hunter2'`.

For passing sensitive configuration into your signer module, you should consider other strategies.

* Pass the path to a configuration file, like, `--signerArg='config=~/alice/signerconfig.json'` 
  with appropriately secure permissions on that file
* Use environment variables. They will be available to your entire process, including within your signer class.
