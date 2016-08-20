var concat = require('gulp-concat');
var gulp = require('gulp');
var less = require('gulp-less');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');

gulp.task('css', function() {
  return gulp.src('assets/less/*.less')
    .pipe(sourcemaps.init())
    .pipe(less({
      paths: [
        'node_modules/bootstrap-less',
      ]
    }))
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/css/'));
});

gulp.task('js', function() {
  return gulp.src([
      'node_modules/jquery/dist/jquery.js',
      'node_modules/bootstrap-less/js/bootstrap.min.js',
    ])
    .pipe(sourcemaps.init())
    .pipe(concat('debconf17.js'))
    .pipe(uglify())
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/js'));
});

gulp.task('default', ['css', 'js']);
