var concat = require('gulp-concat');
var gulp = require('gulp');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');

gulp.task('css', function() {
  return gulp.src('assets/scss/*.scss')
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        includePaths: 'node_modules',
      })
      .on('error', sass.logError)
    )
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/css/'));
});

gulp.task('js', function() {
  return gulp.src([
      'node_modules/jquery/dist/jquery.js',
      'node_modules/bootstrap/node_modules/tether/dist/js/tether.js',
      'node_modules/bootstrap/dist/js/bootstrap.js',
    ])
    .pipe(sourcemaps.init())
    .pipe(concat('debconf17.js'))
    .pipe(uglify())
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/js'));
});

gulp.task('assets', function(){
    gulp.src(
        'assets/*/**/*')
        .pipe(gulp.dest('static/'));
});

gulp.task('default', ['css', 'js', 'assets']);
