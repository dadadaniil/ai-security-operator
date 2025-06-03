package com.sdc.service;

import com.sdc.controller.configuration.auth.CustomUserDetails;
import com.sdc.model.Task;
import com.sdc.model.dto.PageDto;
import com.sdc.model.dto.TaskDto;
import com.sdc.repository.TaskRepository;
import com.sdc.service.annotation.validator.ExistsInDatabaseValidator;
import com.sdc.service.mapper.TaskMapper;
import com.sdc.service.pagination.PageLinks;
import com.sdc.service.pagination.PageLinksGenerator;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.stream.Collectors;

@Service
public class TaskService {
    private final TaskRepository taskRepository;
    private final TaskMapper taskMapper;
    private final ExistsInDatabaseValidator existsInDatabaseValidator;
    private final PageLinksGenerator pageLinksGenerator;

    public TaskService(
        TaskRepository taskRepository,
        TaskMapper taskMapper,
        ExistsInDatabaseValidator existsInDatabaseValidator,
        PageLinksGenerator pageLinksGenerator
    ) {
        this.taskRepository = taskRepository;
        this.taskMapper = taskMapper;
        this.existsInDatabaseValidator = existsInDatabaseValidator;
        this.pageLinksGenerator = pageLinksGenerator;
    }

    public Task saveTask(TaskDto taskDto) {
        Task task = taskMapper.taskDtoToEntity(taskDto);
        taskRepository.save(task);
        return task;
    }

    public TaskDto findTask(Long id) {
        existsInDatabaseValidator.taskValidator(id);
        Task task = taskRepository.getReferenceById(id);
        return taskMapper.taskEntityToDto(task);
    }

    public PageDto<TaskDto> findAllTasks(PageRequest pageRequest) {
        final Page<Task> page = taskRepository.findAll(pageRequest);

        final PageLinks links = pageLinksGenerator.generateLinks("/api/tasks", page);
        return new PageDto<>(
            page.getTotalPages(),
            links.previous(),
            links.next(),
            page
                .getContent()
                .stream()
                .map(taskMapper::taskEntityToDto)
                .collect(Collectors.toList())
        );
    }

    public PageDto<TaskDto> findAllCreatorsTasks(CustomUserDetails userDetails, PageRequest pageRequest) {
        final Page<Task> page = taskRepository.findByCreatorUserId(
            userDetails.getId(),
            pageRequest
        );

        final PageLinks links = pageLinksGenerator.generateLinks("/api/creators/tasks", page);
        return new PageDto<>(
            page.getTotalPages(),
            links.previous(),
            links.next(),
            page
                .getContent()
                .stream()
                .map(taskMapper::taskEntityToDto)
                .collect(Collectors.toList())
        );
    }

    public PageDto<TaskDto> findAllImplementersTasks(CustomUserDetails userDetails, PageRequest pageRequest) {
        final Page<Task> page = taskRepository.findByAssigneesUserId(
            userDetails.getId(),
            pageRequest
        );

        final PageLinks links = pageLinksGenerator.generateLinks("/api/implementors/tasks", page);
        return new PageDto<>(
            page.getTotalPages(),
            links.previous(),
            links.next(),
            page
                .getContent()
                .stream()
                .map(taskMapper::taskEntityToDto)
                .collect(Collectors.toList())
        );
    }
}
