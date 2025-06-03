package com.sdc.controller.web;

import com.sdc.controller.configuration.auth.CustomUserDetails;
import com.sdc.model.dto.GenericResponse;
import com.sdc.model.dto.PageDto;
import com.sdc.model.dto.TaskDto;
import com.sdc.service.TaskService;
import com.sdc.util.Constants;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import static org.springframework.http.HttpStatus.OK;

@RestController
@RequestMapping("/api/creators/tasks")
public class CreatorController {
    private final TaskService taskService;

    public CreatorController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping
    @ResponseStatus(OK)
    @PreAuthorize("hasAuthority('CLIENT')")
    public GenericResponse<PageDto<TaskDto>> getAllCreatorsTasks(
        @AuthenticationPrincipal CustomUserDetails userDetails,
        @RequestParam(defaultValue = Constants.DEFAULT_TASK_PAGE_NUMBER) int pageNum,
        @RequestParam(defaultValue = Constants.DEFAULT_TASK_PAGE_SIZE) int pageSize
    ) {
        final PageRequest pageRequest = PageRequest.of(pageNum - 1, pageSize, Sort.by(Sort.Direction.DESC, "createdDate"));
        return GenericResponse.success(OK, taskService.findAllCreatorsTasks(userDetails, pageRequest));
    }
}
