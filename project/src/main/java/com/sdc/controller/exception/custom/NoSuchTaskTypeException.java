package com.sdc.controller.exception.custom;

public class NoSuchTaskTypeException extends RuntimeException {
    private final long id;

    private NoSuchTaskTypeException(long id) {
        this.id = id;
    }

    public static NoSuchTaskTypeException createWith(long id) {
        return new NoSuchTaskTypeException(id);
    }

    @Override
    public String getMessage() {
        return "Task type with id '" + id + "' does not exist";
    }
}
