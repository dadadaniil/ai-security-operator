package com.sdc.controller.exception.custom;

public class NoSuchTaskException extends RuntimeException {
    private final Long id;

    private NoSuchTaskException(Long id) {
        this.id = id;
    }

    public static NoSuchTaskException createWith(Long id) {
        return new NoSuchTaskException(id);
    }

    @Override
    public String getMessage() {
        return "Task with id '" + id + "' does not exist";
    }
}
