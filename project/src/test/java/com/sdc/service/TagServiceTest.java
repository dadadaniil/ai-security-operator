package com.sdc.service;

import com.sdc.controller.exception.custom.NoSuchTagException;
import com.sdc.model.Tag;
import com.sdc.model.dto.TagDto;
import com.sdc.repository.TagRepository;
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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TagServiceTest {
    @Mock
    private TagRepository tagRepository;
    @Mock
    private PageLinksGenerator pageLinksGenerator;
    @InjectMocks
    private TagService tagService;

    private List<Tag> tags;

    @BeforeEach
    void beforeEach() {
        tags = List.of(
            new Tag(1L, "tag1"),
            new Tag(2L, "tag2"),
            new Tag(3L, "tag3")
        );
    }

    @DisplayName("Test for findAll()")
    @Test
    void testFindAll() {
        final PageRequest pageRequest = PageRequest.of(1, 10);
        when(tagRepository.findAll(pageRequest)).thenReturn(new PageImpl<>(tags));
        when(pageLinksGenerator.generateLinks(anyString(), any())).thenReturn(new PageLinks(null, null));
        List<TagDto> allTags = tagService.findAll(pageRequest).getResults();
        assertEquals(allTags.size(), 3);
    }

    @DisplayName("Test for findTagById()")
    @Test
    void testFindTagById() {
        final long tagId = 2;
        when(tagRepository.findById(tagId)).thenReturn(Optional.of(tags.get((int) tagId - 1)));
        final TagDto tag = tagService.findTagById(tagId);
        assertEquals(tagId, tag.getId());
    }

    @DisplayName("Test for findTagById() with invalid tag ID")
    @Test
    void testFindTagByIdWithInvalidTagId() {
        final long tagId = 4;
        when(tagRepository.findById(tagId)).thenReturn(Optional.empty());
        assertThrows(NoSuchTagException.class, () -> tagService.findTagById(tagId));
    }
}
