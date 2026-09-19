# Asset archaeology

`evidence/assets.json` inventories all supplied `.arc` and `.as` files and their
matching executable string anchors. Container records, compression and decoded
resource types are UNKNOWN. Implement format recovery here independently from
executable reconstruction; keep every transformation reproducible and hashed.
