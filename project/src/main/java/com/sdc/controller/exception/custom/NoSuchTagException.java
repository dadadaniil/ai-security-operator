package com.sdc.controller.exception.custom;

public class NoSuchTagException extends RuntimeException {
    private final long id;

    private NoSuchTagException(long id) {
        this.id = id;
    }

    public static NoSuchTagException createWith(long id) {
        return new NoSuchTagException(id);
    }

    @Override
    public String getMessage() {
        return "Tag with id '" + id + "' does not exist";
    }
}
