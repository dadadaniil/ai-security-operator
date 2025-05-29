package com.sdc.service;

import com.sdc.controller.exception.custom.NoSuchTaskTypeException;
import com.sdc.model.TaskType;
import com.sdc.repository.TaskTypeRepository;
import com.sdc.service.pagination.PageLinks;
import com.sdc.service.pagination.PageLinksGenerator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class TaskTypeServiceTest {
    @Mock
    private TaskTypeRepository taskTypeRepository;
    @Mock
    private PageLinksGenerator pageLinksGenerator;
    @InjectMocks
    private TaskTypeService taskTypeService;

    private List<TaskType> taskTypes;

    @BeforeEach
    void beforeEach() {
        taskTypes = List.of(
            new TaskType(1L, "Individual", "description1"),
            new TaskType(2L, "Team", "description2")
        );
    }

    @DisplayName("Test for findAll()")
    @Test
    void testFindAll() {
        final PageRequest pageRequest = PageRequest.of(1, 10);
        when(taskTypeRepository.findAll(pageRequest)).thenReturn(new PageImpl<>(taskTypes));
        when(pageLinksGenerator.generateLinks(anyString(), any())).thenReturn(new PageLinks(null, null));
        List<TaskType> allTaskTypes = taskTypeService.findAll(pageRequest).getResults();
        assertEquals(taskTypes, allTaskTypes);
    }

    @DisplayName("Test for findTagById()")
    @Test
    void testFindTagById() {
        final long tagId = 2;
        when(taskTypeRepository.findById(tagId)).thenReturn(Optional.of(taskTypes.get((int) tagId - 1)));
        final TaskType tag = taskTypeService.findTagById(tagId);
        assertEquals(tagId, tag.getId());
    }

    @DisplayName("Test for findTagById() with invalid tag ID")
    @Test
    void testFindTagByIdWithInvalidTagId() {
        final long tagId = 4;
        when(taskTypeRepository.findById(tagId)).thenReturn(Optional.empty());
        assertThrows(NoSuchTaskTypeException.class, () -> taskTypeService.findTagById(tagId));
    }
}
