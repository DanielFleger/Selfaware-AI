# Selfaware AI — separate local application, Store boundary candidate

The UCP module is a volatile memory bridge. It does not install, extract or start
this application, and does not keep learning files inside the game.

## Normal installation after Store approval

Install **Selfaware AI** and **Selfaware AI Bridge** through the UCP Store first.
Extract `Selfaware-AI-external-0.2.0.zip` into a permanent folder, run `setup.ps1`
and choose the supported Stronghold Crusader 1.41 installation. The setup creates
the desktop shortcut **Selfaware AI (lokal)**. Use that shortcut to start the
game and its local controller together. Choose SamurAI in a fresh skirmish.

The application uses Documents/Selfaware AI for its runtime, logs and learned
models. It requires no language model, subscription or AI assistant. Learning
means measured local game outcomes and bounded parameter/model updates, not
consciousness or autonomous rewriting of its own program.

The normal external package does not contain an unsigned UCP module and never
replaces the Store's signed module. Game security stays enabled. Until maintainers
have approved and signed the module, this normal installation cannot be tested
as a released Store product.

## Isolated developer review only

`Selfaware-AI-review-0.2.0.zip` additionally contains the unsigned candidate module
and explicitly enables UCP's development security bypass. Use a separate game
copy for review. It is not a signed Store release. Do not replace a working local
installation or its shortcut while reviewing this candidate.

The game module still uses version-specific game structures and guarded hook
signatures for Crusader 1.41. Other executable versions are not supported.
The external application owns all persistent journals and learning data.
