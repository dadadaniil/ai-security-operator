package com.sdc.controller.web;

import com.sdc.model.TaskType;
import com.sdc.model.dto.GenericResponse;
import com.sdc.model.dto.PageDto;
import com.sdc.service.TaskTypeService;
import com.sdc.util.Constants;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.*;

import static org.springframework.http.HttpStatus.OK;

@RestController
@RequestMapping("/api/types")
public class TaskTypeController {
    private final TaskTypeService service;

    public TaskTypeController(TaskTypeService service) {
        this.service = service;
    }

    @GetMapping
    @ResponseStatus(OK)
    public GenericResponse<PageDto<TaskType>> getAllTaskTypes(
        @RequestParam(defaultValue = "1") int pageNum,
        @RequestParam(defaultValue = Constants.DEFAULT_TYPE_PAGE_SIZE) int pageSize
    ) {
        final PageRequest pageRequest = PageRequest.of(pageNum - 1, pageSize);
        final PageDto<TaskType> tags = service.findAll(pageRequest);
        return GenericResponse.success(OK, tags);
    }

    @GetMapping("/{id}")
    @ResponseStatus(OK)
    public GenericResponse<TaskType> getTagById(@PathVariable("id") Long id) {
        return GenericResponse.success(OK, service.findTagById(id));
    }
}
