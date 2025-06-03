package com.sdc.controller.web;

import com.sdc.model.Task;
import com.sdc.model.dto.GenericResponse;
import com.sdc.model.dto.PageDto;
import com.sdc.model.dto.TaskDto;
import com.sdc.service.TaskService;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

import static org.springframework.http.HttpStatus.*;


@RestController
@RequestMapping("/api/tasks")
public class TaskController {
    private final TaskService taskService;

    public TaskController(
        TaskService taskService
    ) {
        this.taskService = taskService;
    }

    @PostMapping
    @ResponseStatus(CREATED)
    public GenericResponse<Map<String, Long>> createTask(@Valid @RequestBody TaskDto taskDto) {
        Task task = taskService.saveTask(taskDto);
        return GenericResponse.successWithId(CREATED, task.getId());
    }

    @GetMapping("/{id}")
    @ResponseStatus(OK)
    public GenericResponse<TaskDto> getTask(@PathVariable("id") Long id) {
        TaskDto taskDto = taskService.findTask(id);
        return GenericResponse.success(OK, taskDto);
    }

    @GetMapping
    @ResponseStatus(OK)
    @PreAuthorize("hasAnyAuthority('CUSTOMER', 'STUDENT')")
    public GenericResponse<PageDto<TaskDto>> getAllTasks(
        @RequestParam(defaultValue = "1") int pageNum,
        @RequestParam(defaultValue = "10") int pageSize
    ) {
        final PageRequest pageRequest = PageRequest.of(pageNum - 1, pageSize, Sort.by(Sort.Direction.DESC, "createdDate"));
        return GenericResponse.success(OK, taskService.findAllTasks(pageRequest));
    }
}
