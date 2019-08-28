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
$ isign --signer=MySigner -o resigned.ipa original.ipa
archived Ipa to /home/alice/resigned.ipa

$ isign --signer=AnotherSigner --signerArg='foo=bar' --signerArg='quux=quuux' \
        -o resigned.ipa original.ipa
archived Ipa to /home/alice/resigned.ipa        
```

## How to write a Signer module

### Where to put it

The module will be invoked by name, much as if it were the result of an `import MySigner` python commans. 
You will need to create an appropriate Python module that is 
available within your `$PYTHONPATH`. See Python documentation for more instructions about that.

### How to write it

A sample Signer module is available [here](TODO).

#### Initialization

Your Python class will be initialized by the following parameters. You may of course ignore them.

* `signer_key_file` - string, an absolute filesystem path to the configured private key.
* `signer_cert_file` - string, an absolute filesystem path to the configured certificate.
* `apple_cert_file` - string, an absolute filesystem path to Apple certificate.
* `signer_args` - dictionary of string keys to string values, extra arguments defined on the command line.

These key and certificate parameters are determined from command-line arguments and configuration conventions. 
See the README or other documentation, or use `isign --help` for more information.
    
You may also pass additional initialization arguments to your Signer class with isign's `--signerArg` command-line  
flag. For instance, in this invocation:

```bash
$ isign --signer=AnotherSigner --signerArg='foo=bar' --signerArg='quux=quuux' \
        -o resigned.ipa original.ipa
```

The `AnotherSigner` class will be initialized with something like the following arguments:

```python
arguments = { 
    'signer_key_file': '/home/alice/.isign/key.pem',
    'signer_cert_file': '/home/alice/.isign/certificate.pem',
    'apple_cert_file': '/path/to/python/lib/site-packages/isign/apple_credentials/applecerts.pem',
    'signer_args': {
        'foo': 'bar',
        'quux': 'quuux'
    }
}
```

Tip: be aware that command line arguments aren't secure. Other users can see the exact command you are running, and 
it might be stored in your shell's `history`. So avoid doing things like `--signerArg='password=hunter2'`.

For passing sensitive configuration into your signer module, you should consider other strategies.

* Pass the path to a configuration file, like, `--signerArg='config=~/alice/signerconfig.json` 
  with appropriately secure permissions on that file
* Use environment variables. They will be available to your entire process, including within your signer class.

#### Interface

Your class, once initialized as on object, must implement these methods:

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

There is only one element of signing that absolutely must remain private: the private key.

Everything else is public knowledge. Your certificate, and Apple's certificates, can be passed around in the clear.

Consequently, if you need to store your keys in an HSM, you can make life easier on yourself by treating some or
all of the certificates as information you pass in as arguments. Your certificate just needs to be paired with the right key.