//! EK-001: exact unsigned coordinate/mask predicate at reference VA 0x00401000.
//! A renderer mask is NOT movement reachability, elevation or line of sight.
//! Candidate pure module for crates/samurai-kern; deliberately not activated in game.
pub fn xy_are_valid(mask: &[u8; 160_000], x: u32, y: u32) -> bool {
    x < 400 && y < 400 && mask[(y * 400 + x) as usize] != 0
}
