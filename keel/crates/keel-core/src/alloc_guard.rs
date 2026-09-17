//! Debug alloc hook. Armed while [`crate::ProcessScope`] is live.

use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;

thread_local! {
    static IN_PROCESS: Cell<bool> = const { Cell::new(false) };
}

pub struct RtAlloc;

unsafe impl GlobalAlloc for RtAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        deny_if_in_process();
        unsafe { System.alloc(layout) }
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }

    unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
        deny_if_in_process();
        unsafe { System.alloc_zeroed(layout) }
    }

    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        deny_if_in_process();
        unsafe { System.realloc(ptr, layout, new_size) }
    }
}

fn deny_if_in_process() {
    IN_PROCESS.with(|c| {
        if c.get() {
            // Allow the panic payload itself or we double-panic and abort.
            if std::thread::panicking() {
                return;
            }
            panic!("keel-core: allocation while in process()");
        }
    });
}

pub fn enter() {
    IN_PROCESS.with(|c| c.set(true));
}

pub fn exit() {
    IN_PROCESS.with(|c| c.set(false));
}
