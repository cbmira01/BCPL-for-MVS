# Distribution manifest

Reserved for the **authoritative source-controlled release inventory**: selection of deployable datasets, **logical tape dataset sequence**, source DASD identifiers resolved against `dspal` where appropriate, position-based tape aliases, destination DASD templates, payload kind, attributes, constituent members, checks and release identity.

**Approved tape alias rule:** logical dataset sequence `n` has tape DSN `BCPL.BTnnnn`, with `nnnn` zero-padded (e.g. `BCPL.BT0003` means logical dataset sequence 3, **not** Hercules `hetmap` physical file 3). `BCPL.BT0001` is reserved for sequential FB80 installation instructions; `BCPL.BT0002` for installation JCL/procedures. Other assignments are release-manifest-driven. Producer and consumer JCL must use the same manifest; the target HLQ is supplied by the receiving MVS site.

See [native compiler distribution and tape naming decisions](../native-cambridge-compiler-distribution-decisions-20261108.md).

The manifest format and authoritative inputs (including `config/dspal.yaml`) are to be specified before producing media. Do not treat this directory as a complete distribution manifest.
