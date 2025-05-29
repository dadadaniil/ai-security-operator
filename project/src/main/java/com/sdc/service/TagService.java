package com.sdc.service;

import com.sdc.controller.exception.custom.NoSuchTagException;
import com.sdc.model.Tag;
import com.sdc.model.dto.PageDto;
import com.sdc.model.dto.TagDto;
import com.sdc.repository.TagRepository;
import com.sdc.service.pagination.PageLinks;
import com.sdc.service.pagination.PageLinksGenerator;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.stream.Collectors;

@Service
public class TagService {
    private final TagRepository repository;
    private final PageLinksGenerator pageLinksGenerator;

    public TagService(TagRepository repository, PageLinksGenerator pageLinksGenerator) {
        this.repository = repository;
        this.pageLinksGenerator = pageLinksGenerator;
    }

    public PageDto<TagDto> findAll(PageRequest pageRequest) {
        final Page<Tag> page = repository.findAll(pageRequest);
        final PageLinks links = pageLinksGenerator.generateLinks("/api/tags", page);

        return new PageDto<>(
            page.getTotalPages(),
            links.previous(),
            links.next(),
            page
                .getContent()
                .stream()
                .map((value) -> new TagDto(value.getId(), value.getTitle()))
                .collect(Collectors.toList())
        );
    }

    public TagDto findTagById(Long id) {
        return repository.findById(id)
            .map((value) -> new TagDto(value.getId(), value.getTitle()))
            .orElseThrow(() -> NoSuchTagException.createWith(id));
    }
}
