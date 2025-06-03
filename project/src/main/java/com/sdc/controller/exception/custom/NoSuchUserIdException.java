package com.sdc.controller.exception.custom;

public class NoSuchUserIdException extends RuntimeException {
    private final long id;

    private NoSuchUserIdException(long id) {
        this.id = id;
    }

    public static NoSuchUserIdException createWith(long id) {
        return new NoSuchUserIdException(id);
    }

    @Override
    public String getMessage() {
        return "User with id '" + id + "' does not exist";
    }
}
