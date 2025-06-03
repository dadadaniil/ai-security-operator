package com.sdc.service;

import com.sdc.controller.exception.custom.NoSuchTaskTypeException;
import com.sdc.model.TaskType;
import com.sdc.model.dto.PageDto;
import com.sdc.repository.TaskTypeRepository;
import com.sdc.service.pagination.PageLinks;
import com.sdc.service.pagination.PageLinksGenerator;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

@Service
public class TaskTypeService {
    private final TaskTypeRepository repository;
    private final PageLinksGenerator pageLinksGenerator;

    public TaskTypeService(TaskTypeRepository repository, PageLinksGenerator pageLinksGenerator) {
        this.repository = repository;
        this.pageLinksGenerator = pageLinksGenerator;
    }

    public PageDto<TaskType> findAll(PageRequest pageRequest) {
        final Page<TaskType> page = repository.findAll(pageRequest);
        final PageLinks links = pageLinksGenerator.generateLinks("/api/types", page);

        return new PageDto<>(
            page.getTotalPages(),
            links.previous(),
            links.next(),
            page.getContent()
        );
    }

    public TaskType findTagById(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> NoSuchTaskTypeException.createWith(id));
    }
}
