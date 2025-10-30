"""
Tests for Progress Manager - Journey Completion Tracking

Part of Phase 5.2: Global Progress Tracker
"""

import pytest
import streamlit as st
from pathlib import Path
from apps.navi_core.progress_manager import (
    load_progress_config,
    mark_page_complete,
    calculate_progress,
    calculate_weighted_progress,
    get_next_unvisited,
    get_pages_for_stage,
    reset_progress,
    get_progress_stats,
    PROGRESS_FILE
)


class TestProgressConfigLoading:
    """Test progress configuration loading."""
    
    def test_progress_file_exists(self):
        """Test that progress.yaml file exists."""
        assert PROGRESS_FILE.exists(), f"Progress file not found: {PROGRESS_FILE}"
    
    def test_load_progress_config_returns_dict(self):
        """Test that load_progress_config returns a dictionary."""
        data = load_progress_config()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_config_has_required_keys(self):
        """Test that config includes required keys."""
        data = load_progress_config()
        required_keys = ["pages", "stages", "weights"]
        
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
    
    def test_config_has_pages(self):
        """Test that pages list is defined."""
        data = load_progress_config()
        pages = data.get("pages", [])
        
        assert isinstance(pages, list)
        assert len(pages) > 0
        assert "Welcome" in pages


class TestPageCompletion:
    """Test page completion tracking."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_mark_page_complete_single(self):
        """Test marking a single page as complete."""
        reset_progress()
        completed = mark_page_complete("Welcome")
        
        assert "Welcome" in completed
        assert len(completed) == 1
    
    def test_mark_page_complete_multiple(self):
        """Test marking multiple pages as complete."""
        reset_progress()
        mark_page_complete("Welcome")
        mark_page_complete("Care Preferences")
        completed = mark_page_complete("Cost Calculator")
        
        assert "Welcome" in completed
        assert "Care Preferences" in completed
        assert "Cost Calculator" in completed
        assert len(completed) == 3
    
    def test_mark_page_complete_duplicate(self):
        """Test that marking same page twice doesn't duplicate."""
        reset_progress()
        mark_page_complete("Welcome")
        completed = mark_page_complete("Welcome")
        
        assert len(completed) == 1
        assert "Welcome" in completed
    
    def test_mark_page_complete_persists_in_session(self):
        """Test that completed pages persist in session_state."""
        reset_progress()
        mark_page_complete("Welcome")
        
        assert "_navi_completed_pages" in st.session_state
        assert "Welcome" in st.session_state["_navi_completed_pages"]


class TestProgressCalculation:
    """Test progress calculation."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_calculate_progress_empty(self):
        """Test progress calculation with no pages completed."""
        reset_progress()
        percent, completed = calculate_progress()
        
        assert percent == 0
        assert len(completed) == 0
    
    def test_calculate_progress_single_page(self):
        """Test progress after completing one page."""
        reset_progress()
        mark_page_complete("Welcome")
        percent, completed = calculate_progress()
        
        assert percent > 0
        assert percent < 100
        assert len(completed) == 1
    
    def test_calculate_progress_all_pages(self):
        """Test progress after completing all pages."""
        reset_progress()
        cfg = load_progress_config()
        
        for page in cfg.get("pages", []):
            mark_page_complete(page)
        
        percent, completed = calculate_progress()
        
        assert percent == 100
        assert len(completed) == len(cfg["pages"])
    
    def test_calculate_progress_percentage_accuracy(self):
        """Test that percentage calculation is accurate."""
        reset_progress()
        cfg = load_progress_config()
        total_pages = len(cfg.get("pages", []))
        
        # Complete half the pages
        for i, page in enumerate(cfg["pages"]):
            if i < total_pages // 2:
                mark_page_complete(page)
        
        percent, completed = calculate_progress()
        expected_percent = int((len(completed) / total_pages) * 100)
        
        assert percent == expected_percent


class TestWeightedProgress:
    """Test weighted progress calculation."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_weighted_progress_empty(self):
        """Test weighted progress with no pages completed."""
        reset_progress()
        percent, completed = calculate_weighted_progress()
        
        assert percent == 0
        assert len(completed) == 0
    
    def test_weighted_progress_high_weight_page(self):
        """Test that high-weight pages contribute more to progress."""
        reset_progress()
        cfg = load_progress_config()
        weights = cfg.get("weights", {})
        
        # Find highest weight page
        highest_weight_page = max(weights, key=weights.get)
        
        mark_page_complete(highest_weight_page)
        percent, _ = calculate_weighted_progress()
        
        # Should be more than simple 1/9 = 11%
        assert percent > 11


class TestNextUnvisited:
    """Test next unvisited page logic."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_get_next_unvisited_at_start(self):
        """Test next unvisited returns first page when none completed."""
        reset_progress()
        next_page = get_next_unvisited()
        
        assert next_page == "Welcome"
    
    def test_get_next_unvisited_after_some(self):
        """Test next unvisited returns correct page after some completed."""
        reset_progress()
        mark_page_complete("Welcome")
        next_page = get_next_unvisited()
        
        assert next_page != "Welcome"
        assert next_page is not None
    
    def test_get_next_unvisited_all_complete(self):
        """Test next unvisited returns None when all pages completed."""
        reset_progress()
        cfg = load_progress_config()
        
        for page in cfg.get("pages", []):
            mark_page_complete(page)
        
        next_page = get_next_unvisited()
        
        assert next_page is None


class TestStagePages:
    """Test stage-to-pages mapping."""
    
    def test_get_pages_for_stage(self):
        """Test retrieving pages for a specific stage."""
        pages = get_pages_for_stage("Awareness")
        
        assert isinstance(pages, list)
        assert len(pages) > 0
    
    def test_get_pages_for_invalid_stage(self):
        """Test retrieving pages for non-existent stage."""
        pages = get_pages_for_stage("NonexistentStage")
        
        assert isinstance(pages, list)
        assert len(pages) == 0


class TestProgressReset:
    """Test progress reset functionality."""
    
    def test_reset_progress_clears_completed(self):
        """Test that reset_progress clears all completed pages."""
        mark_page_complete("Welcome")
        mark_page_complete("Care Preferences")
        
        reset_progress()
        
        assert "_navi_completed_pages" not in st.session_state
    
    def test_reset_progress_zeros_calculation(self):
        """Test that reset_progress zeros out progress calculation."""
        mark_page_complete("Welcome")
        reset_progress()
        
        percent, completed = calculate_progress()
        
        assert percent == 0
        assert len(completed) == 0


class TestProgressStats:
    """Test progress statistics."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_get_progress_stats_structure(self):
        """Test that progress stats returns expected structure."""
        stats = get_progress_stats()
        
        required_keys = [
            "percent",
            "weighted_percent",
            "completed_count",
            "total_count",
            "completed_pages",
            "next_unvisited"
        ]
        
        for key in required_keys:
            assert key in stats
    
    def test_get_progress_stats_accuracy(self):
        """Test that progress stats are accurate."""
        reset_progress()
        mark_page_complete("Welcome")
        mark_page_complete("Care Preferences")
        
        stats = get_progress_stats()
        
        assert stats["completed_count"] == 2
        assert "Welcome" in stats["completed_pages"]
        assert "Care Preferences" in stats["completed_pages"]
        assert stats["percent"] > 0
